from peewee import Model, SqliteDatabase, CharField, DateField, ForeignKeyField
from bcrypt import gensalt, hashpw, checkpw
db = SqliteDatabase('database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField(unique=True)
    hashed_password = CharField(default='')
    salt = CharField(default=str(gensalt()))
    
    def hash_password(password, salt):
        print(password, salt[2:-1])
        return hashpw(str.encode(password), str.encode(salt[2:-1]))
    
    def check_password(password, hashed_password):
        return checkpw(str.encode(password), str.encode(hashed_password))
    
    def __str__(self) -> str:
        return f'User(name={self.username}, salt={self.salt})'
    
class File(BaseModel):
    name = CharField()
    upload_date = DateField()
    owner = ForeignKeyField(User, backref='files')
    
    def __str__(self) -> str:
        return f'Files(name={self.name}, owner={self.owner.username}, upload_date={self.upload_date})'

#db.create_tables([User, File])