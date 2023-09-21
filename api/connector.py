from firebase_admin import firestore_async, credentials
from google.cloud.firestore_v1.base_query import FieldFilter
from mega import Mega
from threading import Thread

import firebase_admin, os

firebase_admin.initialize_app(
    credentials.Certificate(os.path.join('.credentials', 'credentials.json'))
)

#mega = Mega()
#Thread(target=lambda: mega.login('felipefelipe23456@gmail.com', 'mgalomniaco')).start()

class Connector:
    DB = firestore_async.client()
    USERS = DB.collection('leitores')
    BOOKS = DB.collection('livros')
    LENDINGS = DB.collection('emprestimos')
    field_filter = FieldFilter
    #MEGA = mega
    
    def message(message, log=None):
        message = {'message': message}
        if log: 
            message['log'] = log
        return message
    
    def catch_error(func):
        async def wrapper(*args, **kwargs):
            #try:
            return await func(*args, **kwargs)
            #except Exception as e:
            #    return Connector.message('Um erro ocorreu.', str(e))
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