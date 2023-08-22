from flask import Flask, url_for, flash, render_template, request, make_response, redirect, abort, session, send_from_directory, send_file
from markupsafe import escape
import os, datetime
from werkzeug.utils import secure_filename
from pee_wee import User, File, db
app = Flask(__name__)

port = int(os.environ.get("PORT", 5000))

app.secret_key = 'b3d0e0519f154a4b2978d1ed3b861bc6f6dd7d7832b2156955f00102386cb194'

@app.before_request
def before_request():
    db.connect()
    
@app.after_request
def after_request(response):
    db.close()
    return response

def auth_user(user):
    session['logged'] = True
    session['username'] = user.username
    flash('Logado com sucesso!')
    
def logout_user():
    session['logged'] = False
    del session['username']
    flash('Usuário deslogado')
    
def save_file(file):
    user_uploads_path = os.path.join(os.getcwd(), 'uploads', session.get('username'))
    if not os.path.exists(user_uploads_path):
        os.mkdir(user_uploads_path)
    with open(os.path.join(user_uploads_path, file.filename), 'wb') as empty_file:
        for i in file: 
            empty_file.write(i)
        
def login_required(func):
    def inner(*args, **wargs):
        if not session['logged']:
            return redirect(url_for('login'))
        return func(*args, **wargs)
    return inner
    
@app.route('/')
def main():
    kwargs = {
        'logged': session.get('logged', False), 
        'username': session.get('username', None)
    }
    if kwargs['logged']:
        user = User.get(User.username == kwargs['username'])
        kwargs['files'] = [file for file in user.files]
    return render_template('main.html', **kwargs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            user = User.get(User.username == request.form.get('username'))
            if User.check_password(request.form.get('password'), user.hashed_password):
                auth_user(user)
            else:
                flash('Usuário ou senha inválidos')
        except Exception as e:
            print(e)
            flash('Usuário não encontrado')
        return redirect(url_for('main'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            user = User.create(
                username=request.form.get('username')
            )
            user.hashed_password = User.hash_password(request.form.get('password'), user.salt)
            user.save()
            auth_user(user)
        except Exception as e:
            flash('Usuário já existente')
        return redirect(url_for('main'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main'))

@login_required
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if not session.get('logged'):
            return redirect(url_for('login'))
        file = request.files.get('file')
        save_file(file)
        File.create(name=file.filename, upload_date=datetime.datetime.today(), owner=User.get(User.username == session.get('username')).id)
        flash('Arquivo enviado com sucesso!')
        return redirect(url_for('main'))
    return redirect(url_for('main'))

@login_required
@app.route('/<username>/<fileid>/download', methods=['GET'])
def download(username, fileid):
    file = File.get(File.id == fileid)
    return send_from_directory(
        os.path.join(
            'uploads', 
            username
        ),
        file.name,
    )

@app.errorhandler(404)
def page_not_found(error):
    return '<h1>Meio perdido?</h1><p>Página não encontrada, <b>404 NOT FOUND</b></p>', 404

if __name__ == "__main__":
    app.run(port=port)
