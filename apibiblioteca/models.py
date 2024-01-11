from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField
from playhouse.shortcuts import model_to_dict
import secrets, datetime
from .utils import DB

db = SqliteDatabase('database.db')

db.connect()

class Book(Model):
    cdd = CharField()
    assuntos = CharField()
    autor = CharField()
    edicao = CharField()
    editora = CharField()
    estante = CharField()
    prateleira = CharField()
    quantidade = IntegerField()
    titulo = CharField()

    class Meta:
        database = db
        
class Token(Model):
    id = CharField(primary_key=True, default=lambda: secrets.token_hex(16), unique=True)
    date = DateField(default=datetime.datetime.today)

    class Meta:
        database = db
        
    def validate(self):
        today = datetime.datetime.today()
        diff = today - self.date
        if diff.days != 0:
            Token.delete_by_id(self.id)

db.create_tables([Book, Token], safe=True)

print('[GETTING BOOKS FROM FIRESTORE]')
    
for doc in DB.collection('books').stream():
    data = doc.to_dict()
    data.pop('id')
    Book.create(**data)
    
print('[BOOKS GOT]')
