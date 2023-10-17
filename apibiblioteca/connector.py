
from datetime import datetime
from dotenv import load_dotenv
from firebase_admin import credentials, firestore_async, initialize_app
from mega import Mega
from os import environ
import time

load_dotenv()

cred = {key.replace('FIREBASE_', '').lower(): value.replace('\\n', '\n') for key, value in environ.items() if 'FIREBASE' in key}

cred['private_key'] = ''
for key, value in cred.copy().items():
    if 'private_key_n' in key:
        cred['private_key'] += '\n' + value
        cred.pop(key)

initialize_app(
    credentials.Certificate(cred)
)

DB = firestore_async.client()

EMAIL_SENDER = environ.get('EMAIL_SENDER')
EMAIL_PASSWORD = environ.get('EMAIL_PASSWORD')

MEGA = Mega()
login, password = environ.get('MEGA_LOGIN'), environ.get('MEGA_PASSWORD')
print('LOGGING TO MEGA')
while True:
    try:
        MEGA.login(login, password)
        print('LOGIN DONE')
        break
    except Exception as e:
        time.sleep(5)
        print(e)
        print('MEGA LOGIN FAILED. TRYING AGAIN')
    
'''
cdds = {
    28: 'Literatura Infantil/Infanto-Juvenil/Juvenil',
    800: 'Literatura e Retórica',
    900: 'História, Geografia e Biografia',
    300: 'Ciências Sociais',
    0: 'Obras Gerais',
    100: 'Filosofia e psicologia',
    200: 'Religião',
    300: 'Ciências Sociais',
    400: 'Línguas',
    500: 'Ciências Naturais e Matemáticas',
    600: 'Tecnologia e Ciências Aplicadas',
    700: 'Artes',
    30: 'Referencial'
}
'''