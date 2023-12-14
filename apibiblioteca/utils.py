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


def today():
    return datetime.datetime.today().strftime('%d/%m/%y às %H:%M:%S')


def date_to_str(date):
    return date.strftime('%d/%m/%y às %H:%M:%S')


def str_to_date(str):
    return datetime.datetime.strptime(str, '%d/%m/%y às %H:%M:%S')


def get_today_minus_date_days(date):
    today_date = datetime.datetime.today()
    date = datetime.datetime.strptime(date, '%d/%m/%y às %H:%M:%S')
    return (today_date - date).days


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
    'CDD',
    'assuntos',
    'estante',
    'prateleira',
    'quantidade'
]
