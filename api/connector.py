from firebase_admin import firestore_async, credentials, storage

import firebase_admin, os
from google.cloud.firestore_v1.base_query import FieldFilter

firebase_admin.initialize_app(
    credentials.Certificate(os.path.join('.credentials', 'credentials.json')),
    {"storageBucket": "biblioteca-inteligente-72a6c.appspot.com"}
)       

class Connector:
    DB = firestore_async.client()
    USERS = DB.collection('users')
    BOOKS = DB.collection('books')
    bucket = storage.bucket()
    field_filter = FieldFilter
    
    def error(self, error):
        return {'error': error}
    
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