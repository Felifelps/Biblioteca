from asyncio import ensure_future, sleep
from bcrypt import checkpw, gensalt, hashpw
from datetime import datetime
from firebase_admin import credentials, firestore_async, initialize_app
from google.cloud.firestore_v1.base_query import FieldFilter
from mega import Mega
from os.path import join
from threading import Thread
from time import time

initialize_app(
    credentials.Certificate(join('.credentials', 'credentials.json'))
)

mega = Mega()
mega.login('felipefelipe23456@gmail.com', 'mgalomniaco')

class Connector:
    DB = firestore_async.client()
    TRANSACTION = DB.transaction()
    USERS = DB.collection('leitores')
    BOOKS = DB.collection('livros')
    LENDINGS = DB.collection('emprestimos')
    ADM = DB.document('adm/data')
    field_filter = FieldFilter
    admin_data = {}
    MEGA = mega
    
    async def load_admin_data():
        Connector.admin_data = (await Connector.ADM.get()).to_dict()
        return Connector.admin_data
    
    async def save_admin_data():
        await Connector.ADM.update(Connector.admin_data)
        
    def change_admin_password(password):
        salt = gensalt()
        Connector.admin_data['salt'] = salt
        Connector.admin_data['password'] = hashpw(bytes(password, encoding='utf-8'), salt)
        
    def check_admin_password(password):
        return checkpw(bytes(password, encoding='utf-8'), Connector.admin_data['password'])
    
    def message(message, log=None):
        message = {'message': message}
        if log: 
            message['log'] = log
        return message
    
    def today():
        return datetime.today().strftime('%d/%m/%y às %H:%M:%S')
    
    def catch_error(func):
        async def wrapper(*args, **kwargs):
            #try:
            return await func(*args, **kwargs)
            #except Exception as e:
            #    return Connector.message('Um erro ocorreu.', str(e))
        return wrapper
    
    def sync_catch_error(func):
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