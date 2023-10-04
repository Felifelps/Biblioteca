from api.book import Book
from api.connector import Connector
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from quart import Quart, redirect, render_template, request, session, url_for
from random import randint

app = Quart('Biblioteca')
app.config["EXPLAIN_TEMPLATE_LOADING"] = False
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

async def key_in_json(json):
    return json and await Keys.get_email_from_key(json.pop('key', False))

@app.route('/users/', methods=['POST'])
async def all_users():
    if not await key_in_json(await request.get_json()):
        return await render_template('key_required.html')
    return await User.get_users()

@app.route('/user/', methods=['POST'])
async def get_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.get('RG', False)
    if RG: 
        return (await User.get_users()).get(RG, 'User not found')
    return 'Missing RG'

@app.route('/user/new/', methods=['POST'])
async def new_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    try:
        await User.new(**json)
        return 'User created'
    except TypeError as e:
        return f'Invalid json. Missing required parameters:{str(e).split(":")[1]}'
    
@app.route('/user/update/', methods=['POST'])
async def update_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        for field in json:
            if field not in User.fields:
                return 'There is an invalid field: ' + field
        await User.update(RG, **json)
        return 'User updated'
    return 'Missing RG'

@app.route('/user/validate/', methods=['POST'])
async def validate_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        await User.update(RG, valido=True)
        return 'User validated'
    return 'Missing RG'

@app.route('/user/favorite_book/', methods=['POST'])
async def favorite_book_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG: 
        add = json.pop('add', False)
        if add:
            await User.update(RG, valido=True)
        return 'User validated'
    return 'Missing RG'

@app.route('/user/delete/', methods=['POST'])
async def delete_user():
    json = await request.get_json()
    if not await key_in_json(json):
        return await render_template('key_required.html')
    RG = json.pop('RG', False)
    if RG:
        await User.delete(RG)
        return 'User deleted'
    return 'Missing RG'
    

#---------------------- GENERATING API KEY ROUTES ----------------------#
@app.route('/', methods=['GET', 'POST'])
async def register():
    message = None
    if request.method == 'POST':
        email = (await request.form).get('email', None)
        if email not in await Keys.get_keys() and email:
            code = randint(100000, 999999)
            await Email.message(
                email, 
                f'<p>Seu código de confirmação para a api da biblioteca é:</p><h1 style="text-align: center">{code}</h1>', 
                'Biblioteca-Api'
            )
            session['email'] = email
            session['code'] = code
            return redirect(url_for('code'))
        message = 'Email já registrado' if email else 'Email inválido'
    return await render_template('register_email.html', message=message)

@app.route('/code', methods=['GET', 'POST'])
async def code():
    message = None
    if request.method == 'POST':
        code = (await request.form)['code']
        if str(code) == str(session['code']):
            key = await Keys.register_new_key(session['email'])
            await Email.message(
                session['email'], 
                f'<p>Essa é sua chave de api, não a compartilhe publicamente!</p><h1>{key}</h1>', 
                'Biblioteca-Api | Chave'
            )
            return await render_template('key_sended.html')
        message = 'Invalid code!'
    return await render_template('get_code.html', email=session['email'], message=message)

@app.route('/text/', methods=['GET', 'POST'])
async def text():
    if request.method == "POST": 
        print((await request.form)['text'])
    return """<form method="POST"><textarea name="text" style="width: 30em; height: 30em;"></textarea><br><input type="submit"></form> """
