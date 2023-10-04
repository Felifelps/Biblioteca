from api.book import Book
from api.connector import Connector
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from quart import flash, Quart, redirect, render_template, request, session, url_for
from random import randint

app = Quart('Biblioteca')
app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

async def get_form_or_json():
    json = await request.get_json()
    print(json)
    if not json:
        json = {key: value for key, value in (await request.form).items()}
        print(type(json), json)
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
        return (await User.get_users()).get(RG, 'User not found')
    return 'Missing RG'

@app.route('/user/new', methods=['POST'])
async def new_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        if RG in await User.get_users():
            return "An user with this RG already exists"
        try:
            await User.new(**json)
            return 'User created'
        except TypeError as e:
            return f'Missing required parameters:{str(e).split(":")[1]}'
    return 'Missing RG'
    
@app.route('/user/update', methods=['POST'])
async def update_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG:
        if (await User.get_users()).get(RG, False):
            for field in json:
                if field not in User.fields:
                    return 'There is an invalid field: ' + field
            await User.update(RG, **json)
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
        if (await User.get_users()).get(RG, False):
            await User.update(RG, valido=True)
            return 'User validated'
        return 'User not found'
    return 'Missing RG'

@app.route('/user/favorite_book', methods=['POST'])
async def favorite_book_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if RG and book_id:
        if (await User.get_users()).get(RG, False):
            if book_id in await Book.get_books():
                await User.favorite(RG, book_id)
                return 'Favorite updated'
            return 'Book not found'
        return 'User not found'
    return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'

@app.route('/user/delete', methods=['POST'])
async def delete_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG:
        if (await User.get_users()).get(RG, False):
            await User.delete(RG)
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
        return (await Book.get_books()).get(book_id, 'Book not found')
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
        return 'Book created'
    except TypeError as e:
        return f'Missing required parameters:{str(e).split(":")[1]}'
    
@app.route('/book/update', methods=['POST'])
async def update_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if book_id: 
        if (await Book.get_books()).get(book_id, False):
            for field in json:
                if field not in Book.fields:
                    return 'There is an invalid field: ' + field
            await Book.update(book_id, **json)
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
        if (await Book.get_books()).get(book_id, False):
            await Book.delete(book_id)
            return 'Book deleted'
        return 'Book not found'
    return 'Missing book_id'
    

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
        await flash('Email já registrado' if email else 'Email inválido')
    return await render_template('register_email.html')

@app.route('/text', methods=['GET', 'POST'])
async def text():
    if request.method == "POST": 
        print((await request.form)['text'])
    return """<form method="POST"><textarea name="text" style="width: 30em; height: 30em;"></textarea><br><input type="submit"></form> """
