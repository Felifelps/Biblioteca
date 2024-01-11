from bcrypt import checkpw
import datetime
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, initialize_app
from os import environ
import unicodedata

load_dotenv()

cred = {}

for key, value in environ.items():
    if 'FIREBASE' in key:
        cred[key.replace('FIREBASE_', '').lower()] = value.replace('\\n', '\n')

private_key = []
for i in range(0, 28):
    private_key.append(cred.pop(f'private_key_n_{i}'))
cred['private_key'] = '\n'.join(private_key)

initialize_app(
    credentials.Certificate(cred)
)

DB = firestore.client()


def check_admin_login(login: str) -> bool:
    return checkpw(
        bytes(
            login,
            encoding='utf-8'
        ),
        bytes(
            environ.get('ADMIN_LOGIN'),
            encoding='utf-8'
        )
    )


def check_admin_password(password: str) -> bool:
    return checkpw(
        bytes(
            password,
            encoding='utf-8'
        ),
        bytes(
            environ.get('ADMIN_PASSWORD'),
            encoding='utf-8'
        )
    )


def message(message):
    return {'message': message}


def standardize_search_string(string):
    list = []
    for c in unicodedata.normalize('NFD', string.lower()):
        if unicodedata.category(c) != 'Mn':
            list.append(c)
    return ''.join(list)


BOOK_REQUIRED_FIELDS = [
    'titulo',
    'autor',
    'editora',
    'edicao',
    'cdd',
    'assuntos',
    'estante',
    'prateleira',
    'quantidade'
]
