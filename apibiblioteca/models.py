from peewee import SqliteDatabase, Model, CharField, IntegerField
import secrets

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

    class Meta:
        database = db
        
db.connect()

db.create_tables([Book, Token])

