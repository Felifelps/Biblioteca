from .models import db, Book, Token, model_to_dict
from .utils import (
    check_admin_login,
    check_admin_password,
    BOOK_REQUIRED_FIELDS,
    message,
    standardize_search_string,
)
from os import environ
import pandas as pd
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

JSON = {}

app = Flask('Biblioteca')
cors = CORS(app, resources={r"*": {"origins": "https://bibliotecamilagres.netlify.app"}})

app.secret_key = environ.get('SECRET_KEY')


@app.before_request
def connect_data():
    global JSON
    JSON = request.get_json()
    if not JSON:
        form = request.form
        JSON = {key: value for key, value in form.items()}
    if request.url.split('/')[-1] in [
            'update',
            'new',
            'delete',
            'data'
            ]:
        token_valid = JSON and JSON.get('token', False)
        token_valid = token_valid and Token.get_by_id(
            JSON.pop('token')
        )
        if not token_valid:
            return jsonify(message('token invalid'))


@app.after_request
def commit_and_close_data(response):
    db.commit()
    return response


@app.post('/books/length')
def books_len():
    return jsonify({'len': len(Book.select())})


@app.post('/books/page')
def get_book_page():
    page = JSON.get('page', False)
    if not page or int(page) > (len(Book.select())//24) + 1:
        return jsonify('Page out of the range' if page else 'Missing page parameter')
    start = (24 * (int(page) - 1))
    result = Book.select().limit((start + 24) - start).offset(start)
    books = {}
    for i, data in enumerate(map(lambda x: model_to_dict(x), result)):
        books[str(i + start + 1)] = data
    return jsonify(books)


@app.post('/books/search')
def search_books():
    all_books = list(map(lambda x: model_to_dict(x), Book.select()))
    for book in all_books.copy():
        for key, search in JSON.items():
            if key not in BOOK_REQUIRED_FIELDS:
                return jsonify(f'{key} not a valid parameter')
            search = standardize_search_string(search)
            value = standardize_search_string(book[key])
            if value == search or search in value:
                continue
            all_books.pop(all_books.index(book))
    return jsonify(all_books)


@app.post('/books/field_values')
def books_field_values():
    field = JSON.get('field', False)
    if not field or field not in BOOK_REQUIRED_FIELDS:
        return jsonify('Invalid field' if field else 'Missing field')
    values = set([getattr(book, field) for book in Book.select()])
    return jsonify(list(values))


@app.post('/book/new')
def new_book():
    missing_fields = list(
        filter(
            lambda x: x not in JSON.keys(),
            BOOK_REQUIRED_FIELDS
        )
    )
    if missing_fields == []:
        print(model_to_dict(Book.create(**JSON)))
        return jsonify(message(f'Book{"" if int(JSON["quantidade"]) == 1 else "s"} created'))
    return jsonify(message(f'Missing required parameters: {"".join(missing_fields)}'))


@app.post('/book/update')
def update_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return jsonify(message('Missing book_id'))
    try:
        book = Book.get_by_id(int(book_id))
    except Exception as e:
        return jsonify(message('Book not found'))
    for key, value in JSON.items():
        exec(f"book.{key} = value")
    book.save()
    return jsonify(message('Book updated'))


@app.post('/book/delete')
def delete_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return jsonify(message('Missing book_id'))
    message_text = 'Book not found' if not Book.delete_by_id(int(book_id)) else 'Book deleted'
    return jsonify(message(message_text))


@app.post('/admin/login')
def admin_login():
    login = JSON.get('login', False)
    if not login:
        return jsonify(message('Missing login'))
    password = JSON.get('password', False)
    if not password:
        return jsonify(message('Missing password'))
    if not check_admin_login(login):
        return jsonify(message('Login invalid'))
    if not check_admin_password(password):
        return jsonify(message('Password invalid'))
    return jsonify({'token': Token.create().id})

@app.post('/admin/check')
def admin_check():
    token = JSON.get('token', False)
    if not token:
        return jsonify(message('Missing token'))
    result = True
    try:
        Token.get_by_id(token)
    except Exception as e:
        result = False
    return jsonify(message(result))
    


@app.post('/get/data')
def return_data():
    df = pd.DataFrame(data=[model_to_dict(book) for book in Book.select()])
    df.to_excel('livros.xlsx', index=True)
    return send_file('livros.xlsx', as_attachment=True)


@app.errorhandler(500)
def handle_error(error):
    db.session_rollback()
    return jsonify(message(f'An error ocurred: {str(error)}'), 500)
