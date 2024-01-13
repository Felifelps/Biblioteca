from peewee import SqliteDatabase, Model, CharField, IntegerField, DateField
from playhouse.shortcuts import model_to_dict
import secrets, datetime

db = SqliteDatabase('database.db')

db.connect()

class Book(Model):
    id = IntegerField(primary_key=True, unique=True)
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
