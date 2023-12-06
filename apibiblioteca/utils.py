from bcrypt import checkpw, gensalt, hashpw
import datetime
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from mega import Mega
from os import environ
import json

load_dotenv()

cred = {key.replace('FIREBASE_', '').lower(): value.replace('\\n', '\n') for key, value in environ.items() if 'FIREBASE' in key}

private_key = []
for i in range(0, 28):
    private_key.append(cred.pop(f'private_key_n_{i}'))
cred['private_key'] = '\n'.join(private_key)

initialize_app(
    credentials.Certificate(cred)
)

DB = firestore.client()

EMAIL_SENDER = environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')

print('[LOGGING TO MEGA]')
MEGA = Mega()
MEGA.login(environ.get('MEGA_LOGIN'), environ.get('MEGA_PASSWORD'))
print('[LOGIN DONE]')
    
def today():
    return datetime.datetime.today().strftime('%d/%m/%y às %H:%M:%S')  

def date_to_str(date):
    return date.strftime('%d/%m/%y às %H:%M:%S') 

def str_to_date(str):
    return datetime.datetime.strptime(str, '%d/%m/%y às %H:%M:%S') 

def get_today_minus_date_days(date):
    return (datetime.datetime.today() - datetime.datetime.strptime(date, '%d/%m/%y às %H:%M:%S')).days

def check_admin_login(login: str) -> bool:
    return checkpw(bytes(login, encoding='utf-8'), bytes(environ.get('ADMIN_LOGIN'), encoding='utf-8'))
def check_admin_password(password: str) -> bool:
    return checkpw(bytes(password, encoding='utf-8'), bytes(environ.get('ADMIN_PASSWORD'), encoding='utf-8'))

def message(message):
    return {'message': message}

DATA_REQUIRED_FIELDS = {
    'user': [
        "RG",
        "nome",
        "data_nascimento",
        "local_nascimento",
        "email",
        "CEP",
        "tel_pessoal",
        "residencia"
    ],
    'book': [
        'titulo',
        'autor',
        'editora',
        'edicao',
        'CDD',
        'assuntos',
        'estante',
        'prateleira'
    ]
}

MESSAGES = {
    'user_registered': lambda username: f'''
<h1>Olá {username}!</h1>
<p>Seus dados foram enviados para análise.</p>
<p>Te enviaremos uma reposta por esse email assim que analisarmos.</p>
    ''',
    
    'user_validated': lambda username: f'''
<h1>Olá {username}!</h1>
<p>Seus dados foram validados!</p>
<p>Faça login em nosso <a>site (colocar link)</a> com seu RG e comece a ler</p>
''',

    'lending_renewed': lambda username, booktitle: f'''
<h1>Olá {username}!</h1>
<p>Seu empréstimo do livro {booktitle} foi renovado!</p>
<p>Agora você tem mais 10 dias para lê-lo. Aproveite!</p>
''',
    
    'book_lended': lambda username, booktitle: f'''
<h1>Olá {username}!</h1>
<p>Seu empréstimo do livro {booktitle} foi concluído!</p>
<b>Venha buscá-lo em até dois dias úteis. Caso contrário, o empréstimo será cancelado.</b>
''',
    
    'lending_finalized_not_get': lambda username, booktitle: f'''
<h1>Olá {username}!</h1>
<p>Seu empréstimo do livro {booktitle} foi cancelado devido o fim do prazo de busca do livro.</p>
''',
    
    'days_to_renew_or_return': lambda username, booktitle, days_left: f'''
<h1>Olá {username}!</h1>
<p>Você tem {days_left} dia{"s" if days_left != 1 else ""} para devolver o livro {booktitle}</p>    

''',

    'multa_number': lambda username, booktitle, multa: f'''
<h1>Olá {username}!</h1>
<p>Seu prazo de entrega do livro {booktitle} expirou {"a 1 dia" if multa == 0.1 else f"fazem {multa*10:.0f} dias"} :(</p>
Multa acumulada: R${multa:.2f}
<p>Venha à biblioteca para pagar a multa e devolver ou renovar o livro</p>
'''
}