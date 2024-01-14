"""
This module contains the Flask application for the Biblioteca.
It includes the following functionalities:
- Connecting to the database
- Handling requests for books data
- Handling requests for admin login and token validation
- Handling requests for returning data in excel format
- Error handling
"""


from os import environ
import pandas as pd
from quart import Quart, request, send_file
from quart_cors import cors
from playhouse.shortcuts import model_to_dict
from .models import db, Book, Token
from .utils import (
    check_admin_login,
    check_admin_password,
    BOOK_REQUIRED_FIELDS,
    message,
    standardize_search_string,
)

app = Quart('Biblioteca')
app = cors(app, allow_origin='https://bibliotecamilagres.netlify.app')

app.secret_key = environ.get('SECRET_KEY')
app.JSON = {}


@app.before_request
async def connect_data():
    """ Connect to the database and validate the request. """
    app.JSON = await request.get_json()
    if not app.JSON:
        form = await request.form
        app.JSON = dict(form.items())
    if request.url.split('/')[-1] in [
            'update',
            'new',
            'delete',
            'data'
            ]:
        try:
            if not (app.JSON and app.JSON.get('token', False)):
                raise Exception('Not valid!')
            Token.get_by_id(
                app.JSON.pop('token')
            )
        except Exception as e:
            return message('token invalid')


@app.after_request
async def commit_and_close_data(response):
    """ Commit and close the database connection. """
    db.commit()
    return response


@app.post('/books/length')
async def books_len():
    """ Return the number of books in the database. """
    return {'len': len(Book.select())}


@app.post('/books/page')
async def get_book_page():
    """ Return a page of books from the database. """
    page = app.JSON.get('page', False)
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
    """ Search for books in the database based on the provided parameters. """
    all_books = list(map(lambda x: model_to_dict(x), Book.select()))
    for book in all_books.copy():
        for key, search in app.JSON.items():
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
    """ Return the unique values for a given field in the books table. """
    field = app.JSON.get('field', False)
    if not field or field not in BOOK_REQUIRED_FIELDS:
        return 'Invalid field' if field else 'Missing field'
    values = set([getattr(book, field) for book in Book.select()])
    return list(values)


@app.post('/book/new')
async def new_book():
    """ Create a new book in the database. """
    missing_fields = list(
        filter(
            lambda x: x not in app.JSON.keys(),
            BOOK_REQUIRED_FIELDS
        )
    )
    if missing_fields == []:
        print(model_to_dict(Book.create(**JSON)))
        message_s = "" if int(JSON["quantidade"]) == 1 else "s"
        return message(f'Book{message_s} created')
    return message(f'Missing required parameters: {"".join(missing_fields)}')


@app.post('/book/update')
async def update_book():
    """ Update a book in the database. """
    book_id = app.JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    try:
        book = Book.get_by_id(int(book_id))
    except Exception as e:
        return message('Book not found')
    for key, value in app.JSON.items():
        setattr(book, key, value)
    book.save()
    return message('Book updated')


@app.post('/book/delete')
async def delete_book():
    """ Delete a book from the database. """
    book_id = app.JSON.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    return message(
        'Book not found' if not Book.delete_by_id(
            int(book_id)
        ) else 'Book deleted')


@app.post('/admin/login')
async def admin_login():
    """ Authenticate an admin user. """
    login = app.JSON.get('login', False)
    if not login:
        return message('Missing login')
    password = app.JSON.get('password', False)
    if not password:
        return message('Missing password')
    if not check_admin_login(login):
        return message('Login invalid')
    if not check_admin_password(password):
        return message('Password invalid')
    return {'token': Token.create().id}


@app.post('/admin/check')
async def admin_check():
    """ Check if a given token is valid. """
    token = app.JSON.get('token', False)
    if not token:
        return message('Missing token')
    result = True
    try:
        Token.get_by_id(token)
    except Exception as e:
        print(e)
        result = False
    return message(result)


@app.post('/get/data')
async def return_data():
    """ Return the books data in excel format. """
    df = pd.DataFrame(data=[model_to_dict(book) for book in Book.select()])
    df.to_excel('livros.xlsx', index=True)
    return await send_file('livros.xlsx', as_attachment=True)


@app.errorhandler(500)
async def handle_error(error):
    """ Handle 500 Internal Server Error. """
    db.session_rollback()
    return message(f'An error ocurred: {str(error)}'), 500
