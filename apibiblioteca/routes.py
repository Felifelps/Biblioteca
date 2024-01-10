from .models import Book, Token, db
from peewee import fn
from .data import DATA
from .utils import (
    check_admin_login,
    check_admin_password,
    BOOK_REQUIRED_FIELDS,
    date_to_str,
    message,
    standardize_search_string,
    str_to_date,
    today
)
import datetime
from os import environ
import pandas as pd
from quart import Quart, request, send_file
from quart_cors import cors
from playhouse.shortcuts import model_to_dict
import secrets

JSON = {}

app = Quart('Biblioteca')
app = cors(app, allow_origin='https://bibliotecamilagres.netlify.app')

app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = environ.get('SECRET_KEY')


@app.before_request
async def connect_data():
    db.connect()
    global JSON
    JSON = await request.get_json()
    if not JSON:
        form = await request.form
        JSON = {key: value for key, value in form.items()}
    if request.url.split('/')[-1] in [
            #'update',
            #'new',
            #'delete',
            #'data'
            ]:
        token_valid = JSON and JSON.get('token', False)
        token_valid = token_valid and Token.get_by_id(
            JSON.pop('token')
        )
        if not token_valid:
            return message('token invalid')


@app.after_request
async def commit_and_close_data(response):
    db.close()
    return response


@app.post('/books/length')
async def books_len():
    return {'len': len(Book.select())}


@app.post('/books/page')
async def get_book_page():
    page = JSON.get('page', False)
    if not page or int(page) > (len(Book.select())//24) + 1:
        return 'Page out of the range' if page else 'Missing page parameter'
    start = (24 * (int(page) - 1))
    result = Book.select().limit((start + 24) - start).offset(start)
    books = {}
    for i, data in enumerate(map(lambda x: model_to_dict(x), result)):
        books[str(i + start + 1)] = data
    return books


@app.post('/books/search')
async def search_books():
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


@app.post('/books/field_values')
async def books_field_values():
    field = JSON.get('field', False)
    if not field or field not in BOOK_REQUIRED_FIELDS:
        return 'Invalid field' if field else 'Missing field'
    values = set([getattr(book, field) for book in Book.select()])
    return list(values)


@app.post('/book/new')
async def new_book():
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


@app.post('/book/update')
async def update_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    try:
        book = Book.get_by_id(int(book_id))
        print(model_to_dict(book))
    except Exception as e:
        return message('Book not found')
    for key, value in JSON.items():
        exec(f"book.{key} = value")
    book.save()
    return message('Book updated')


@app.delete('/book/delete')
async def delete_book():
    book_id = JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    book = DATA['books'].get(book_id)
    if not book:
        return message('Book not found')
    DATA['books'].pop(book_id)
    return message('Book deleted')


@app.post('/admin/login')
async def admin_login():
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
    token = secrets.token_hex(32)
    DATA['tokens'][token] = date_to_str(
        str_to_date(today()) + datetime.timedelta(days=1)
    )
    return {'token': token}


@app.post('/admin/check')
async def admin_check():
    token = JSON.get('token', False)
    if not token:
        return message('Missing token')
    return message(token in DATA['tokens'])


@app.post('/get/data')
async def return_data():
    df = pd.DataFrame(data=DATA['books'])
    df.T.to_excel('livros.xlsx', index=True)
    return await send_file('livros.xlsx', as_attachment=True)


@app.errorhandler(500)
async def handle_error(error):
    return message(f'An error ocurred: {str(error)}'), 500
