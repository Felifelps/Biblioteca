from peewee import *

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

db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db
        
class Bookcase(BaseModel):
    name = CharField()

class Shelf(BaseModel):
    name = CharField()
    bookshelf = ForeignKeyField(Bookcase, backref='shelfs')

class CDD(BaseModel):
    id = IntegerField(unique=True)
    subject = CharField()
    
class Book(BaseModel):
    title = CharField()
    author = CharField()
    publish_company = CharField()
    cdd = ForeignKeyField(CDD)
    edition = IntegerField()
    amount = IntegerField()
    subjects = CharField(default="")
    bookcase = ForeignKeyField(Bookcase)
    shelf = ForeignKeyField(Shelf, backref='books')
    

db.connect()
'''db.create_tables([
    Bookcase,
    Book,
    Shelf,
    CDD
])'''
db.close()