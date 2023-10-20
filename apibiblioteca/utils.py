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

print(json.dumps(cred, indent=4))

initialize_app(
    credentials.Certificate(cred)
)

DB = firestore.client()

EMAIL_SENDER = environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')

DATA_REQUIRED_FIELDS = {
    'user': [
        "RG",
        "nome",
        "data_nascimento",
        "local_nascimento",
        "email",
        "CEP",
        "tel_pessoal",
        "residencia",
        "profissao",
        "tel_profissional",
        "escola",
        "curso_serie"
    ],
    'book': [
        'id',
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

print('[LOGGING TO MEGA]')
MEGA = Mega()
MEGA.login(environ.get('MEGA_LOGIN'), environ.get('MEGA_PASSWORD'))
print('[LOGIN DONE]')
        

def today():
    return datetime.datetime.today().strftime('%d/%m/%y às %H:%M:%S')  

def check_admin_password(password: str) -> bool:
    return checkpw(bytes(password, encoding='utf-8'), bytes(environ.get('ADMIN_PASSWORD'), encoding='utf-8'))