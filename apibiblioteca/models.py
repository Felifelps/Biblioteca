"""Library Management System using Peewee ORM

This module provides a simple library management system
using the Peewee ORM. It defines two models, Book and Token,
and a function to validate the token.

"""

import datetime
import secrets
import os
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    IntegerField,
    DateField
)

DATABASE_WAS_ALERADY_CREATED = os.path.exists('database.db')

db = SqliteDatabase('database.db')

db.connect()


class Book(Model):
    """
    The Book model represents a book in the library and has
    the following fields:

    - id: unique identifier for the book
    - cdd: CD-DIB code for the book
    - assuntos: subjects of the book
    - autor: author of the book
    - edicao: edition of the book
    - editora: publisher of the book
    - estante: shelf where the book is located
    - prateleira: row where the book is located
    - quantidade: quantity of copies of the book available
    in the library
    - titulo: title of the book

    Attributes:
    - id (IntegerField): unique identifier for the book
    - cdd (CharField): CD-DIB code for the book
    - assuntos (CharField): subjects of the book
    - autor (CharField): author of the book
    - edicao (CharField): edition of the book
    - editora (CharField): publisher of the book
    - estante (CharField): shelf where the book is located
    - prateleira (CharField): row where the book is located
    - quantidade (IntegerField): quantity of copies of the book
    available in the library
    - titulo (CharField): title of the book
    """
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
        """
        MetaData Peewee Class
        """
        database = db


class Token(Model):
    """The Token model represents a token used to validate the user's
    session and has the following fields:

    - id: unique identifier for the token
    - date: date when the token was generated

    Attributes:
    - id (CharField): unique identifier for the token
    - date (DateField): date when the token was generated

    Methods:
    - validate: checks if the token is still valid by comparing
    the current date with the date when the token was generated.
    If the difference between the two dates is not zero, the token
    is deleted.

    """
    id = CharField(
        primary_key=True,
        default=lambda: secrets.token_hex(16),
        unique=True
    )
    date = DateField(default=datetime.datetime.today)

    class Meta:
        """
        MetaData Peewee Class
        """
        database = db

    def validate(self):
        """
        Checks if the token is still valid by comparing
        the current date with the date when the token was
        generated. If the difference between the two dates
        is not zero, the token is deleted.
        """
        today = datetime.datetime.today()
        diff = today - self.date
        if diff.days != 0:
            Token.delete_by_id(self.id)


db.create_tables([Book, Token], safe=True)
