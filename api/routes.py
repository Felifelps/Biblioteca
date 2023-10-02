from api.book import Book
from api.email import Email
from api.files import Files
from api.keys import Keys
from api.lending import Lending
from api.user import User
from quart import Quart, redirect, render_template, request, url_for

app = Quart('Biblioteca')

@app.route('/register', methods=['GET', 'POST'])
async def register():
    if request.method == 'POST':
        form = await request.form
        return await Keys.register_new_key(form['email'])
    return await render_template('register_email.html')


@app.route('/text/', methods=['GET', 'POST'])
async def text():
    if request.method == "POST": 
        print((await request.form)['text'])
    return """<form method="POST"><textarea name="text" style="width: 30em; height: 30em;"></textarea><br><input type="submit"></form> """
