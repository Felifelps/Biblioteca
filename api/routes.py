from api.book import Book
from api.connector import Connector
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from asyncio import ensure_future
from datetime import datetime
from os.path import exists, join
from quart import flash, Quart, render_template, request, send_file
from quart_cors import cors

# TODO: DOCUMENTAR TODAS AS VIEWS E REVER A DOCUMENTAÇÃO GERAL
# TODO: TESTES COM ASYNC PYTEST
#548e0783ca4b16a090b1c5dc38973557
app = Quart('Biblioteca')
app = cors(app, allow_origin='*')

app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

async def get_form_or_json():
    json = await request.get_json()
    if not json:
        json = {key: value for key, value in (await request.form).items()}
    return json

async def key_in_json(json):
    return json and json.get('key', False) and await Keys.get_email_from_key(json.pop('key'))

@app.post('/users')
async def all_users():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await User.get_users()

@app.post('/user')
async def get_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if RG:
        return await User.get(RG, 'User not found')
    return 'Missing RG'

@app.post('/user/new')
async def new_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not RG: 
        return 'Missing RG'
    if await User.get(RG):
        return "An user with this RG already exists"
    try:
        await User.new(**json)
        return 'User created'
    except TypeError as e:
        return f'Missing required parameters:{str(e).split(":")[1]}'

@app.post('/user/update')
async def update_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return 'Missing RG'
    user = await User.get(RG, to_dict=False)
    if not user:
        return 'User not found'
    for key, value in json.items():
        if key not in user.fields:
            return 'There is an invalid field: ' + key
        user[key] = value
    await user.save()
    return 'User updated'

@app.post('/user/validate')
async def validate_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG: 
        return 'Missing RG'
    user = await User.get(RG, to_dict=False)
    if not user:
        return 'User not found'
    user.valido = True
    await user.save()
    return 'User validated'

@app.post('/user/favorite_book')
async def favorite_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'
    user = await User.get(RG, to_dict=False)
    if not (user and await Book.query('id', '==', book_id)):
        return f'{"User" if not user else "Book"} not found'
    if book_id in user.favoritos:
        user.favoritos.pop(user.favoritos.index(book_id))
    else:
        user.favoritos.append(book_id)
    await user.save()
    return 'Favorite updated'

@app.post('/user/delete')
async def delete_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return 'Missing RG'
    user = await User.get(RG, to_dict=False)
    if not user:
        return 'User not found'
    await user.delete()
    return 'User deleted'

@app.post('/books')
async def all_books():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await Book.get_books()

@app.post('/book')
async def get_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.get('book_id', False)
    if not book_id: 
        return 'Missing book_id'
    return await Book.get(book_id, 'Book not found')   

@app.post('/book/new')
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
    
@app.post('/book/update')
async def update_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id: 
        return 'Missing book_id'
    book = await Book.get(book_id, to_dict=False)
    if not book:
        return 'Book not found'
    for key, value in json.items():
        if key not in book.fields:
            return 'There is an invalid field: ' + key
        book[key] = value
    await book.save()
    return 'Book updated'

@app.post('/book/delete')
async def delete_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id:
        return 'Missing book_id'
    book = await Book.get(book_id, to_dict=False)
    if not book:
        return 'Book not found'
    await book.delete()
    return 'Book deleted'
    
@app.post('/lendings')
async def all_lendings():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return await Lending.get_lendings()

@app.post('/lending')
async def get_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.get('lending_id', False)
    if not lending_id: 
        return 'Missing lending_id'
    lending = await Lending.get(lending_id, to_dict=False)
    if not lending:
        return 'Lending not found'
    if not lending.data_finalizacao:
        lending_limit = 20 if lending.renovado else 10
        lending_time = (datetime.today() - datetime.strptime(lending.data_emprestimo, '%d/%m/%y às %H:%M:%S')).days
        if not lending.pego and lending_time > 2:
            user = await User.get(lending.leitor, to_dict=False)
            if not user: 
                return "User not found"
            user.livro = False
            await user.save()
            book = await Book.get(lending.livro, to_dict=False)
            if not user: 
                return "Book not found"
            book.leitor = False
            await book.save()
            lending.data_finalizacao = Connector.today()
        elif lending_time > lending_limit:
            lending.multa = 0.10 * (lending_time - lending_limit)
        await lending.save()
    return lending.to_dict()

@app.post('/lending/new')
async def new_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'
    user = await User.get(RG, to_dict=False)
    if not (user and not user['livro']):
        return 'User already has a book' if user else 'User not found'
    book = await Book.get(book_id, to_dict=False)
    if not (book and not book['leitor']):
        return 'Book was already taken' if book else 'Book not found'
    try:
        await Lending.new(RG, book_id)
        user.livro = book_id
        book.leitor = RG
        await user.save(), await book.save()
        return 'Book lended'
    except TypeError as e:
        return f'Missing required parameters:{str(e).split(":")[1]}'
    
@app.post('/lending/update')
async def update_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.pop('lending_id', False)
    if not lending_id:
        return 'Missing lending_id'
    lending = await Lending.get(lending_id, to_dict=False)
    if not lending:
        return 'Lending not found'
    if not lending.data_finalizacao:
        return 'Lending already finalizated'
    for key, value in json.items():
        if key not in ['pego', 'renovado']:
            return 'There is an invalid field: ' + key
        elif not value:
            return 'This field just accept the true value.'
    lending[key] = value
    await lending.save()
    return 'Lending updated' 

@app.post('/user/files/send')
async def send_user_files():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not (RG and await User.get(RG)): 
        return 'Missing RG' if  not RG else 'User not found'
    files = await request.files
    RG_frente = files.get('RG_frente', False)
    if not RG_frente: 
        return 'Missing RG_frente'
    RG_verso = files.get('RG_verso', False)
    if not RG_verso: 
        return 'Missing RG_verso'
    comprovante = files.get('comprovante', False)
    if not comprovante: 
        return 'Missing comprovante'
    async def paralel():
        for file, description in {RG_frente: 'RG_frente', RG_verso: 'RG_verso', comprovante: 'comprovante'}.items():
            with open(Files.temp(file.filename), 'wb') as local_file:
                for i in file:
                    local_file.write(i)
            await Files.upload(file.filename, f'{RG}-{description}.' + file.filename.split('.')[-1])
    ensure_future(paralel())
    return 'Enviando arquivos'

@app.post('/user/files/get')
async def get_user_file():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not (RG and await User.get(RG)): 
        return 'Missing RG' if  not RG else 'User not found'
    file_type = json.get('file_type', False)
    if file_type not in ['RG_frente', 'RG_verso', 'comprovante']: 
        return 'file_type must be one of this: RG_frente, RG_verso or comprovante' if file_type else 'Missing file_type'
    try:
        for filename in Files.files:
            if RG in filename and file_type in filename:
                
                if not exists(Files.temp(filename)):
                    await Files.download(filename)
                ensure_future(Files.future_remove(Files.temp(filename)))
                return await send_file(join('temp', filename))
        return 'File not found'
    except PermissionError as e:
        return 'An error ocurred'

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

@app.route('/text/', methods=['GET', 'POST'])
async def text():
    if request.method == "POST": 
        print((await request.form)['text'])
    return """<form method="POST"><textarea name="text" style="width: 30em; height: 30em;"></textarea><br><input type="submit"></form> """

@app.route('/', methods=['GET', 'POST'])
async def test():
    if request.method == "POST":
        print('Hi')
    return """
<style>
    input {
        font-size: 16px;
    }
</style>
<form method="POST" action="/user/files/send" enctype="multipart/form-data">
    <input type="hidden" value="548e0783ca4b16a090b1c5dc38973557" name="key">
    <br>
    <br>
    <input type="text" value="2018125194-4" name="RG">
    <br>
    <br>
    <label for="RG_frente">RG_Frente</label>
    <input type="file" id="RG_frente" name="RG_frente">
    <br>
    <br>
    <label for="RG_verso">RG_verso</label>
    <input type="file" id="RG_verso" name="RG_verso">
    <br>
    <br>
    <label for="comprovante">comprovante</label>
    <input type="file" id="comprovante" name="comprovante">
    <br>
    <br>
    <input type="submit">
</form> 
    """
    
@app.route('/get', methods=['GET', 'POST'])
async def test2():
    if request.method == "POST":
        pass
    return """
<style>
    input {
        font-size: 16px;
    }
</style>
<form method="POST" action="/user/files/get" enctype="multipart/form-data">
    <input type="hidden" value="548e0783ca4b16a090b1c5dc38973557" name="key">
    <input type="text" value="2018125194-4" name="RG">
    <br>
    <br>
    <select name="file_type">
        <option value="RG_frente">RG_frente</option>
        <option value="RG_verso">RG_verso</option>
        <option value="comprovante">comprovante</option>
    </select>
    <br>
    <br>
    <input type="submit">
</form> 
    """