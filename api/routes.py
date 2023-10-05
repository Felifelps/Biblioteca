from api.book import Book
from api.connector import Connector
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from datetime import datetime
from firebase_admin.firestore_async import firestore
from quart import flash, Quart, redirect, render_template, request, session, url_for
from random import randint

# TODO: DOCUMENTAR TODAS AS VIEWS
app = Quart('Biblioteca')
app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

async def get_form_or_json():
    json = await request.get_json()
    if not json:
        json = {key: value for key, value in (await request.form).items()}
    return json

async def key_in_json(json):
    return json and json.get('key', False) and await Keys.get_email_from_key(json.pop('key'))

@app.route('/users', methods=['POST'])
async def all_users():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await User.get_users()

@app.route('/user', methods=['POST'])
async def get_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if RG:
        return await User.get(RG, 'User not found')
    return 'Missing RG'

@app.route('/user/new', methods=['POST'])
async def new_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        if await User.get(RG):
            try:
                await User.new(**json)
                return 'User created'
            except TypeError as e:
                return f'Missing required parameters:{str(e).split(":")[1]}'
        return "An user with this RG already exists"
    return 'Missing RG'
    
@app.route('/user/update', methods=['POST'])
async def update_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG:
        user = await User.get(RG, to_dict=False)
        if user:
            for key, value in json.items():
                if key not in user.fields:
                    return 'There is an invalid field: ' + key
                user[key] = value
            await user.save()
            return 'User updated'
        return 'User not found'
    return 'Missing RG'

@app.route('/user/validate', methods=['POST'])
async def validate_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        user = await User.get(RG, to_dict=False)
        if user:
            user.valido = True
            await user.save()
            return 'User validated'
        return 'User not found'
    return 'Missing RG'

@app.route('/user/favorite_book', methods=['POST'])
async def favorite_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if RG and book_id:
        user = await User.get(RG, to_dict=False)
        if user and await Book.query('id', '==', book_id):
            if book_id in user.favoritos:
                user.favoritos.pop(user.favoritos.index(book_id))
            else:
                user.favoritos.append(book_id)
            await user.save()
            return 'Favorite updated'
        return f'{"User" if not user else "Book"} not found'
    return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'

@app.route('/user/delete', methods=['POST'])
async def delete_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG:
        user = await User.get(RG, to_dict=False)
        if user:
            await user.delete()
            return 'User deleted'
        return 'User not found'
    return 'Missing RG'

@app.route('/books', methods=['POST'])
async def all_books():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await Book.get_books()

@app.route('/book', methods=['POST'])
async def get_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.get('book_id', False)
    if book_id: 
        return await Book.get(book_id, 'Book not found')
    return 'Missing book_id'

@app.route('/book/new', methods=['POST'])
async def new_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    #number of copies
    n = json.pop('n', 1)
    try:
        for i in range(int(n)):
            await Book.new(**json)
        return f'Book{"" if n == 1 else "s"} created'
    except TypeError as e:
        return f'Missing required parameters:{str(e).split(":")[1]}'
    
@app.route('/book/update', methods=['POST'])
async def update_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if book_id: 
        book = await Book.get(book_id, to_dict=False)
        if book:
            for key, value in json.items():
                if key not in book.fields:
                    return 'There is an invalid field: ' + key
                book[key] = value
            await book.save()
            return 'Book updated'
        return 'Book not found'
    return 'Missing book_id'

@app.route('/book/delete', methods=['POST'])
async def delete_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if book_id:
        book = await Book.get(book_id, to_dict=False)
        if book:
            await book.delete()
            return 'Book deleted'
        return 'Book not found'
    return 'Missing book_id'
    
@app.route('/lendings', methods=['POST'])
async def all_lendings():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await Lending.get_lendings()

@app.route('/lending', methods=['POST'])
async def get_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.get('lending_id', False)
    if lending_id: 
        return (await Lending.get_lendings()).get(lending_id, 'Lending not found')
    return 'Missing lending_id'

@app.route('/lending/new', methods=['POST'])
async def new_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    id_livro = json.pop('id_livro', False)
    if RG and id_livro:
        user = (await User.get_users()).get(RG, False)
        if user and not user['livro']:
            book = await Book.get(id_livro, False)
            if book and not book['leitor']:
                try:
                    await Lending.new(RG, id_livro)
                    await User.update(RG, livro=id_livro)
                    await Book.update(id_livro, leitor=RG)
                    return 'Book lended'
                except TypeError as e:
                    return f'Missing required parameters:{str(e).split(":")[1]}'
            return 'Book was already taken' if book else 'Book not found'
        return 'User already has a book' if user else 'User not found'
    return f'Missing: {"" if RG else "RG"}{", " if RG == id_livro else ""}{"" if id_livro else "id_livro"}'
    
@app.route('/lending/update', methods=['POST'])
async def update_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.pop('lending_id', False)
    if lending_id: 
        lending = (await Lending.get_lendings()).get(lending_id, False)
        if (await Lending.get_lendings()).get(lending_id, False):
            for field in json:
                if field not in Lending.fields:
                    return 'There is an invalid field: ' + field
            await Lending.update(lending_id, **json)
            lending_limit = 20 if lending['renovado'] else 10
            lending_time = (datetime.today() - datetime.strptime(lending['data_emprestimo'], '%d/%m/%y às %H:%M:%S')).days
            if not lending['pego'] and lending_time > 2:
                await User.update(lending['leitor'], livro=lending['livro'])
                await Book.update(lending['livro'], leitor=lending['leitor'])
                await Lending.finalize(lending_id)
                lending['data_finalizacao'] = Connector.today()
            elif lending_time > lending_limit:
                await Lending.update(lending_id, multa=0.10 * (lending_time - lending_limit))
                lending['multa'] = 0.10 * lending_time
            return lending
        return 'Lending not found'
    return 'Missing lending_id'

@app.route('/lending/delete', methods=['POST'])
async def delete_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.pop('lending_id', False)
    if lending_id:
        if (await Lending.get_lendings()).get(lending_id, False):
            await Lending.delete(lending_id)
            return 'Lending deleted'
        return 'Lending not found'
    return 'Missing lending_id'

#---------------------- GENERATING API KEY ROUTES ----------------------#
@app.route('/register/key', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email', None)
        password = form.get('password', None)
        if email and email not in await Keys.get_keys():
            if password and await Connector.check_admin_password(password):
                key = await Keys.register_new_key(email)
                await Email.message(
                    email, 
                    f'<p>Essa é sua chave de api, não a compartilhe publicamente!</p><h1>{key}</h1>', 
                    'Biblioteca-Api | Chave'
                )
                return await render_template('key_sended.html')
            await flash('Senha inválida')
        if not password:
            await flash('Email já registrado' if email else 'Email inválido')
    return await render_template('register_email.html')

@app.route('/text/', methods=['GET', 'POST'])
async def text():
    if request.method == "POST": 
        print((await request.form)['text'])
    return """<form method="POST"><textarea name="text" style="width: 30em; height: 30em;"></textarea><br><input type="submit"></form> """
