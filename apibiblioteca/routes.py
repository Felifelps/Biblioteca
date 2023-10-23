from .data import DATA
from .email import Email
from .files import Files
from .keys import Keys
from .utils import check_admin_password, DATA_REQUIRED_FIELDS, today
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
    return json and json.get('key', False) and Keys.get_email_from_key(json.pop('key'))

@app.before_request
async def connect_data():
    await DATA.connect()
    
@app.after_request
async def commit_and_close_data(response):
    await DATA.commit_and_close()
    return response

@app.post('/users')
async def all_users():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return DATA['users']

@app.post('/user')
async def get_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if RG:
        return DATA['users'].get(RG, 'User not found')
    return 'Missing RG'

@app.post('/user/new')
async def new_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not RG: 
        return 'Missing RG'
    if DATA['users'].get(RG):
        return "An user with this RG already exists"
    missing_fields = list(filter(lambda x: x not in json.keys(), DATA_REQUIRED_FIELDS['user']))
    if missing_fields == []:
        json.update({
            "data_cadastro": today(),
            "valido": False,
            "favoritos": [],
            "livro": False
        })
        DATA['users'].update({RG: json})
        return 'User created'
    return f'Missing required parameters: {str(missing_fields)}'

@app.post('/user/update')
async def update_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return 'Missing RG'
    user = DATA['users'].get(RG, False)
    if not user:
        return 'User not found'
    for key, value in json.items():
        if key not in DATA_REQUIRED_FIELDS['user']:
            return 'There is an invalid field: ' + key
        user.update({key: value})
    DATA['users'].update({RG: json})
    return 'User updated'

@app.post('/user/validate')
async def validate_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG: 
        return 'Missing RG'
    user = DATA['users'].get(RG, False)
    if not user:
        return 'User not found'
    user.update({'valido': True})
    DATA['users'].update({RG: json})
    return 'User validated'

@app.post('/user/favorite')
async def favorite_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'
    user = DATA['users'].get(RG, False)
    if not (user and DATA['books'].get(str(book_id), False)):
        return f'{"User" if not user else "Book"} not found'
    if book_id in user['favoritos']:
        user['favoritos'].pop(user['favoritos'].index(book_id))
    else:
        user['favoritos'].append(book_id)
    DATA['users'].update({RG: user})
    return 'Favorite updated'

@app.post('/user/delete')
async def delete_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return 'Missing RG'
    user = DATA['users'].get(RG, False)
    if not user:
        return 'User not found'
    DATA['users'].pop(RG)
    return 'User deleted'

@app.post('/books')
async def all_books():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return DATA['books']

@app.post('/book')
async def get_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.get('book_id', False)
    if not book_id: 
        return 'Missing book_id'
    return DATA['books'].get(book_id, 'Book not found')   

@app.post('/book/new')
async def new_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    #number of copies
    n = json.pop('n', 1)
    missing_fields = list(filter(lambda x: x not in json.keys(), DATA_REQUIRED_FIELDS['book']))
    if missing_fields == []:
        json.update({
            "leitor": False
        })
        for i in range(n):
            DATA['books'].update({str(len(DATA['books'])): json})
        return f'Book{"" if n == 1 else "s"} created'
    return f'Missing required parameters: {str(missing_fields)}'
    
@app.post('/book/update')
async def update_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id: 
        return 'Missing book_id'
    book = DATA['books'].get(book_id, False)
    if not book:
        return 'Book not found'
    for key, value in json.items():
        if key not in DATA_REQUIRED_FIELDS['book']:
            return 'There is an invalid field: ' + key
        book.update({key: value})
    DATA['books'].update({str(book_id): json})
    return 'Book updated'

@app.post('/book/delete')
async def delete_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id:
        return 'Missing book_id'
    book = DATA['books'].get(book_id, to_dict=False)
    if not book:
        return 'Book not found'
    DATA['books'].pop(book_id)
    return 'Book deleted'
    
@app.post('/lendings')
async def all_lendings():
    if not await key_in_json(await get_form_or_json()):
        return await render_template('key_required.html')
    return DATA['lendings']

@app.post('/lending')
async def get_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.get('lending_id', False)
    if not lending_id: 
        return 'Missing lending_id'
    lending = DATA['lendings'].get(lending_id, False)
    if not lending:
        return 'Lending not found'
    if not lending['data_finalizacao']:
        lending_limit = 20 if lending['renovado'] else 10
        lending_time = (datetime.today() - datetime.strptime(lending['data_emprestimo'], '%d/%m/%y às %H:%M:%S')).days
        if not lending['pego'] and lending_time > 2:
            user = DATA['user'].get(lending['leitor'], False)
            if not user: 
                return "User not found"
            book = DATA['books'].get(lending['livro'], False)
            if not book: 
                return "Book not found"
            lending['data_finalizacao'] = today()
            DATA['users'][user].update({'livro': False})
            DATA['books'][book].update({'leitor': False})
        elif lending_time > lending_limit:
            lending['multa'] = 0.10 * (lending_time - lending_limit)
        DATA['lendings'].update({lending_id: lending})
    return lending

@app.post('/lending/new')
async def new_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}'
    user = DATA['users'].get(RG, False)
    if not (user and not user['livro']):
        return 'User already has a book' if user else 'User not found'
    book = DATA['books'].get(book_id, False)
    if not (book and not book['leitor']):
        return 'Book was already taken' if book else 'Book not found'
    lending_id = str(len(DATA['lendings']))
    DATA['lendings'].update({ 
        lending_id: {
            'id': lending_id,
            'leitor': RG,
            'livro': book_id,
            'multa': 0,
            'data_emprestimo': today(),
            'renovado': False,
            'data_finalizacao': False
        }
    })
    DATA['users'][RG].update({'livro': book_id})
    DATA['books'][book_id].update({'leitor': RG})
    return 'Book lended'

@app.post('/user/files/send')
async def send_user_files():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not (RG and DATA['users'].get(RG, False)): 
        return 'Missing RG' if not RG else 'User not found'
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
    if not (RG and DATA['users'].get(RG, False)): 
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
@app.route('/register_key', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email', None)
        password = form.get('password', None)
        if email and email not in Keys.get_keys().keys():
            if password and check_admin_password(password):
                key = Keys.register_new_key(email)
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