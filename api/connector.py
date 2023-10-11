"""
# api.connector
This module aims to: 
    \n-> initialize the Firebase application 
    \n-> log in to the Mega Api
    \n-> gather essential constants and methods for other files in the Connector class
"""

from bcrypt import checkpw, gensalt, hashpw
from datetime import datetime
from dotenv import load_dotenv
from firebase_admin import credentials, firestore_async, initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter
from mega import Mega
from os import environ, getenv
from os.path import join

load_dotenv()

cred = {key.replace('FIREBASE_', '').lower(): value.replace('\\n', '\n') for key, value in environ.items() if 'FIREBASE' in key}

cred['private_key'] = ''
for key, value in cred.copy().items():
    if 'private_key_n' in key:
        cred['private_key'] += '\n' + value
        cred.pop(key)

print(cred)

initialize_app(
    credentials.Certificate(cred)
)

MEGA = Mega()
MEGA.login('felipefelipe23456@gmail.com', 'mgalomniaco')

class Connector:
    """
    #   api.connector.Connector
    This class stores some recurrent constants of the database and some methods
    used for manipulate the adm data and catch errors.
    
    - DB: firestore_async.client() -> References the database
    - USERS: DB.collection('leitores') -> References the user collection
    - BOOKS: DB.collection('livros') -> References the books collection
    - LENDINGS: DB.collection('emprestimos') -> References the lendings collection
    - ADM: DB.document('adm/data')  -> References the adm document
    - API_KEYS = DB.collection('keys') -> References the keys collection
    - field_filter: FieldFilter -> Used for querys
    - admin_data: {} -> Stores admin data
    
    """
    DB = firestore_async.client()
    USERS = DB.collection('leitores')
    BOOKS = DB.collection('livros')
    LENDINGS = DB.collection('emprestimos')
    API_KEYS = DB.collection('keys')
    ADM = DB.document('adm/data')
    field_filter = FieldFilter
    admin_data = {}
    
    async def load_admin_data() -> dict:
        """
        This function returns the admin data stored on the
        firestore database.
        """
        Connector.admin_data = (await Connector.ADM.get()).to_dict()
        return Connector.admin_data
    
    async def save_admin_data() -> None:
        """
        This function saves on firestore the data stored on Connector.admin_data
        """
        await Connector.ADM.update(Connector.admin_data)
        
    def change_admin_password(password: str) -> None:
        """
        This function changes password on Connector.admin_data to a new hashed 
        string using a new salt 
        """
        salt = gensalt()
        Connector.admin_data['salt'] = salt
        Connector.admin_data['password'] = hashpw(bytes(password, encoding='utf-8'), salt)
        
    async def check_admin_password(password: str) -> bool:
        """
        This function checks if the password parameter corresponds to the hashed
        password stored in Connector.admin_data
        """
        await Connector.load_admin_data()
        return checkpw(bytes(password, encoding='utf-8'), Connector.admin_data['password'])
    
    def message(message: str, log: str=None) -> dict:
        """
        This function return a json like dict for general api responses
        """
        message = {'message': message}
        if log: 
            message['log'] = log
        return message
    
    def today() -> str:
        """
        Returns the current date using the pattern '%d/%m/%y às %H:%M:%S'
        """
        return datetime.today().strftime('%d/%m/%y às %H:%M:%S')
    
    def catch_error(func):
        """
        Decorator to handle exceptions on async functions
        """
        async def wrapper(*args, **kwargs):
            #try:
            return await func(*args, **kwargs)
            #except Exception as e:
            #    return Connector.message('Um erro ocorreu.', str(e))
        return wrapper
    
    def sync_catch_error(func):
        """
        Decorator to handle exceptions on sync functions
        """
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                return Connector.message('Um erro ocorreu.', str(e))
        return wrapper

    
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