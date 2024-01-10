from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField
import secrets, datetime

db = SqliteDatabase('database.db')

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
    date = CharField(default=lambda: datetime.datetime.today().strftime('%d/%m/%y'))

    class Meta:
        database = db
        
    def is_valid(self):
        today = datetime.datetime.today()
        date = datetime.datetime.strptime(self.date, 
        
db.connect()

db.create_tables([Book, Token], safe=True)

import pandas

dt = pandas.read_json('data.json')

data = dt.to_dict()

for i in data['books'].values():
    i.update({'cdd': i['CDD']})
    i.pop('CDD')
    a = Book.create(**i)
    a.save()
    

    

db.close()

