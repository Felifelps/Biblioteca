from api.book import Book
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from quart import Quart, redirect, render_template, request, session, url_for
from random import randint

app = Quart('Biblioteca')
app.secret_key = "1d8bb19a04c8dc8bbe4e73eeffdb9796"

@app.route('/', methods=['GET', 'POST'])
async def register():
    message = None
    if request.method == 'POST':
        email = (await request.form)['email']
        if email in await Keys.get_keys():
            message = 'Email já registrado'
        else:
            code = randint(100000, 999999)
            await Email.message(
                email, 
                f'<p>Seu código de confirmação para a api da biblioteca é:</p><h1 style="text-align: center">{code}</h1>', 
                'Biblioteca-Api'
            )
            session['email'] = email
            session['code'] = code
            return redirect(url_for('code'))
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
