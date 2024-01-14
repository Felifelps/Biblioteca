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
            return message('token invalid')


@app.after_request
def commit_and_close_data(response):
    db.commit()
    return response


@app.route('/books/length', methods=['POST', 'OPTIONS'])
def books_len():
    return {'len': len(Book.select())}


@app.route('/books/page', methods=['POST', 'OPTIONS'])
def get_book_page():
    page = JSON.get('page', False)
    if not page or int(page) > (len(Book.select())//24) + 1:
        return 'Page out of the range' if page else 'Missing page parameter'
    start = (24 * (int(page) - 1))
    result = Book.select().limit((start + 24) - start).offset(start)
    books = {}
    for i, data in enumerate(map(lambda x: model_to_dict(x), result)):
        books[str(i + start + 1)] = data
    return books


@app.route('/books/search', methods=['POST', 'OPTIONS'])
def search_books():
    all_books = list(map(lambda x: model_to_dict(x), Book.select()))
    for book in all_books.copy():
        for key, search in JSON.items():
            if key not in BOOK_REQUIRED_FIELDS:
                return f'{key} not a valid parameter'
            search = standardize_search_string(search)
            value = standardize_search_string(book[key])
            if value == search or search in value:
                continue
            all_books.pop(all_books.index(book))
    return all_books


@app.route('/books/field_values', methods=['POST', 'OPTIONS'])
def books_field_values():
    field = JSON.get('field', False)
    if not field or field not in BOOK_REQUIRED_FIELDS:
        return 'Invalid field' if field else 'Missing field'
    values = set([getattr(book, field) for book in Book.select()])
    return list(values)


@app.route('/book/new', methods=['POST', 'OPTIONS'])
def new_book():
    missing_fields = list(
        filter(
            lambda x: x not in JSON.keys(),
            BOOK_REQUIRED_FIELDS
        )
    )
    if missing_fields == []:
        print(model_to_dict(Book.create(**JSON)))
        return message(f'Book{"" if int(JSON["quantidade"]) == 1 else "s"} created')
    return message(f'Missing required parameters: {"".join(missing_fields)}')


@app.route('/book/update', methods=['POST', 'OPTIONS'])
def update_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    try:
        book = Book.get_by_id(int(book_id))
    except Exception as e:
        return message('Book not found')
    for key, value in JSON.items():
        exec(f"book.{key} = value")
    book.save()
    return message('Book updated')


@app.route('/book/delete', methods=['POST', 'OPTIONS'])
def delete_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    message_text = 'Book not found' if not Book.delete_by_id(int(book_id)) else 'Book deleted'
    return message(message_text)


@app.route('/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    login = JSON.get('login', False)
    if not login:
        return message('Missing login')
    password = JSON.get('password', False)
    if not password:
        return message('Missing password')
    if not check_admin_login(login):
        return message('Login invalid')
    if not check_admin_password(password):
        return message('Password invalid')
    return {'token': Token.create().id}

@app.route('/admin/check', methods=['POST', 'OPTIONS'])
def admin_check():
    token = JSON.get('token', False)
    if not token:
        return message('Missing token')
    result = True
    try:
        Token.get_by_id(token)
    except Exception as e:
        result = False
    return message(result)



@app.route('/get/data', methods=['POST', 'OPTIONS'])
def return_data():
    df = pd.DataFrame(data=[model_to_dict(book) for book in Book.select()])
    df.to_excel('livros.xlsx', index=True)
    return send_file('livros.xlsx', as_attachment=True)


@app.errorhandler(500)
def handle_error(error):
    db.session_rollback()
    return message(f'An error ocurred: {str(error)}'), 500
