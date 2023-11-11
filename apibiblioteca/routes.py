from .data import DATA
from .email import Email
from .files import Files
from .keys import Keys
from .utils import check_admin_password, DATA_REQUIRED_FIELDS, MESSAGES, message, today
from asyncio import ensure_future
from datetime import datetime
from os.path import exists, join
from quart import flash, Quart, render_template, request, send_file
from quart_cors import cors

# TODO: DOCUMENTAR TODAS AS VIEWS E REVER A DOCUMENTAÇÃO GERAL
# TODO: TESTES COM ASYNC PYTEST
#548e0783ca4b16a090b1c5dc38973557
app = Quart('Biblioteca')
app = cors(app, allow_origin='*', allow_headers='*', allow_methods='*')

app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

async def get_form_or_json():
    json = await request.get_json()
    if not json:
        form = await request.form
        json = {key: value for key, value in form.items()}
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
        return DATA['users'].get(RG, message('User not found'))
    return message('Missing RG')

@app.post('/user/new')
async def new_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not RG: 
        return message('Missing RG')
    if DATA['users'].get(RG):
        return message('An user with this RG already exists') 
    
    missing_fields = list(filter(lambda x: x not in json.keys(), DATA_REQUIRED_FIELDS['user']))
    if len(missing_fields) > 0:
        return message(f'Missing required parameters: {str(missing_fields)}')
    json.update({
        "data_cadastro": today(),
        "valido": False,
        "favoritos": [],
        "livro": False
    })
    
    files = await request.files
    RG_frente = files.get('RG_frente', False)
    if not RG_frente: 
        return message('Missing RG_frente')
    RG_verso = files.get('RG_verso', False)
    if not RG_verso: 
        return message('Missing RG_verso')
    comprovante = files.get('comprovante', False)
    if not comprovante: 
        return message('Missing comprovante')
    
    DATA['users'].update({RG: json})
    await Email.message(
        json['email'], 
        MESSAGES['user_registered'](json['nome']),
        "Biblioteca - Dados registrados"
    )
    
    async def paralel():
        print(f'[UPLOADING USER({json["nome"]}) DATA]')
        for file, description in {RG_frente: 'RG_frente', RG_verso: 'RG_verso', comprovante: 'comprovante'}.items():
            with open(Files.temp(file.filename), 'wb') as local_file:
                for i in file:
                    local_file.write(i)
            await Files.upload(file.filename, f'{RG}-{description}.' + file.filename.split('.')[-1])
        print(f'[DATA UPLOADED]')
    ensure_future(paralel())   
    
    return message('User created')
    
@app.post('/user/update')
async def update_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return message('Missing RG')
    user = DATA['users'].get(RG, False)
    if not user:
        return message('User not found')
    for key, value in json.items():
        if key not in DATA_REQUIRED_FIELDS['user']:
            return message('There is an invalid field: ' + key)
        user.update({key: value})
    DATA['users'].update({RG: json})
    return message('User updated')

@app.post('/user/validate')
async def validate_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG: 
        return message('Missing RG')
    user = DATA['users'].get(RG, False)
    if not user:
        return message('User not found')
    user.update({'valido': True})
    DATA['users'].update({RG: json})
    await Email.message(
        user['email'], 
        MESSAGES['user_validated'](json['nome']),
        "Biblioteca - Conta validada!"
    )
    return message('User validated')

@app.post('/user/favorite')
async def favorite_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return message(f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}')
    user = DATA['users'].get(RG, False)
    if not (user and DATA['books'].get(str(book_id), False)):
        return message(f'{"User" if not user else "Book"} not found')
    if book_id in user['favoritos']:
        user['favoritos'].pop(user['favoritos'].index(book_id))
    else:
        user['favoritos'].append(book_id)
    DATA['users'].update({RG: user})
    return message('Favorite updated')

@app.post('/user/delete')
async def delete_user():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if not RG:
        return message('Missing RG')
    user = DATA['users'].get(RG, False)
    if not user:
        return message('User not found')
    DATA['users'].pop(RG)
    return message('User deleted')

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
        return message('Missing book_id')
    return DATA['books'].get(book_id, message('Book not found'))   

@app.post('/book/new')
async def new_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    #number of copies
    n = json.pop('n', 1)
    missing_fields = list(filter(lambda x: x not in json.keys(), DATA_REQUIRED_FIELDS['book']))
    if missing_fields == [] or missing_fields == ['id']:
        json.update({
            "copies": [{"copy_id": i, "leitor": False} for i in range(1, n + 1)]
        })
        DATA['books'].update({str(len(DATA['books'])): json})
        return message(f'Book{"" if n == 1 else "s"} created')
    missing_fields.pop(0)
    return message(f'Missing required parameters: {str(missing_fields)}')
    
@app.post('/book/update')
async def update_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id: 
        return message('Missing book_id')
    book = DATA['books'].get(book_id, False)
    if not book:
        return message('Book not found')
    for key, value in json.items():
        if key not in DATA_REQUIRED_FIELDS['book']:
            return message('There is an invalid field: ' + key)
        book.update({key: value})
    DATA['books'].update({str(book_id): json})
    return message('Book updated')

@app.post('/book/delete')
async def delete_book():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    book_id = json.pop('book_id', False)
    if not book_id:
        return message('Missing book_id')
    book = DATA['books'].get(book_id, to_dict=False)
    if not book:
        return message('Book not found')
    DATA['books'].pop(book_id)
    return message('Book deleted')
    
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
        return message('Missing lending_id')
    return DATA['lendings'].get(lending_id, message('Lending not found'))
    
@app.post('/lending/new')
async def new_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    book_id = json.pop('book_id', False)
    if not (RG and book_id):
        return message(f'Missing: {"" if RG else "RG"}{", " if RG == book_id else ""}{"" if book_id else "book_id"}')
    user = DATA['users'].get(RG, False)
    if not user or user['livro']:
        return message('User already has a book' if user else 'User not found')
    book = DATA['books'].get(book_id, False)
    if not book: 
        return message('Book not found')
    availables = [copy['leitor'] for copy in book['copies']]
    if all(availables):
        return message('All the copies of this book were already taken.')
    copy_index = availables.index(False)
    lending_id = str(len(DATA['lendings']))
    DATA['lendings'].update({ 
        lending_id: {
            'id': lending_id,
            'leitor': RG,
            'livro': book_id,
            'multa': 0,
            'data_emprestimo': today(),
            'pego': False,
            'data_finalizacao': False
        }
    })
    user.update({'livro': book_id})
    book['copies'][copy_index].update({'leitor': RG})
    await Email.message(
        user['email'], 
        MESSAGES['book_lended'],
        f'Biblioteca - {book["titulo"]} emprestado'    
    )
    return message('Book lended')

@app.post('/lending/book_get')
@app.post('/lending/book_returned')
@app.post('/lending/renew')
@app.post('/lending/pay')
async def update_lending():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    lending_id = json.get('lending_id', False)
    if not lending_id: 
        return message('Missing lending_id')
    lending = DATA['lendings'].get(lending_id, False)
    if not lending:
        return message('Lending not found')
    url = request.url_rule.rule
    update = {}
    if 'book_' in url:
        update = {'pego': today() if 'get' in url else False}
    elif 'renew' in url:
        update = {'pego': today()}
        await Email.message(
            DATA['user'][lending['leitor']]['email'], 
            MESSAGES['lending_renewed'],
            "Biblioteca - Livro renovado"
        )
    elif 'pay' in url:
        update = {'multa': 0}
    DATA['lendings'][lending_id].update(update)
    return message('Lending updated')

@app.post('/user/files/get')
async def get_user_file():
    json = await get_form_or_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if not (RG and DATA['users'].get(RG, False)): 
        return message('Missing RG' if  not RG else 'User not found')
    file_type = json.get('file_type', False)
    if file_type not in ['RG_frente', 'RG_verso', 'comprovante']: 
        return message('file_type must be one of this: RG_frente, RG_verso or comprovante' if file_type else 'Missing file_type')
    try:
        for filename in Files.files:
            if RG in filename and file_type in filename:
                
                if not exists(Files.temp(filename)):
                    await Files.download(filename)
                ensure_future(Files.future_remove(Files.temp(filename)))
                return await send_file(join('temp', filename))
        return message('File not found')
    except PermissionError as e:
        return message('An error ocurred')

#---------------------- GENERATING API KEY ROUTES ----------------------#
@app.route('/register_key', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        email = form.get('email', False)
        password = form.get('password', False)
        if email and email not in DATA['keys'].keys():
            if password and check_admin_password(password):
                key = Keys.register_new_key(email)
                await Email.message(
                    email, 
                    f'<p>Essa é sua chave de api, não a compartilhe publicamente!</p><h1>{key}</h1>', 
                    'Biblioteca - Chave de api'
                )
                return await render_template('key_sended.html')
            await flash('Senha inválida')
        else:
            await flash('Email já registrado' if email else 'Email inválido')
    return await render_template('register_email.html')

@app.errorhandler(500)
async def handle_error(error):
    return message(f'An error ocurred: {str(error)}', 500)