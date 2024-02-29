"""This module contains various utility functions for the project.

Functions:
- check_admin_login: checks if the given login matches
the admin login
- check_admin_password: checks if the given password
matches the admin password
- message: returns a dictionary with a single key-value
pair for the message field
- standardize_search_string: standardizes a search string
by removing diacritics and converting to lowercase

Variables:
- BOOK_REQUIRED_FIELDS: a list of required fields for a book
document in the Firestore database

"""

import os
import unicodedata

from bcrypt import checkpw
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY')

DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')

DATABASE_USER = os.environ.get('DATABASE_USER')

DATABASE_HOST = os.environ.get('DATABASE_HOST')

DATABASE_PORT = os.environ.get('DATABASE_PORT')

DATABASE_NAME = os.environ.get('DATABASE_NAME')

def check_admin_login(login: str) -> bool:
    """Check if the given login matches the admin login."""
    return checkpw(
        bytes(login, encoding='utf-8'),
        bytes(os.environ.get('ADMIN_LOGIN'), encoding='utf-8')
    )


def check_admin_password(password: str) -> bool:
    """Check if the given password matches the admin password."""
    return checkpw(
        bytes(password, encoding='utf-8'),
        bytes(os.environ.get('ADMIN_PASSWORD'), encoding='utf-8')
    )


def message(message_text):
    """
    Return a dictionary with a single key-value pair
    for the message field.
    """
    return {'message': message_text}


def standardize_search_string(string):
    """
    Standardize a search string by removing diacritics
    and converting to lowercase.
    """
    normalized_chars = []
    for c in unicodedata.normalize('NFD', string.lower()):
        if unicodedata.category(c) != 'Mn':
            normalized_chars.append(c)
    return ''.join(normalized_chars)


# List of required fields for a book document in the Firestore database
BOOK_REQUIRED_FIELDS = [
    'titulo',
    'autor',
    'editora',
    'edicao',
    'cdd',
    'assuntos',
    'estante',
    'prateleira',
    'quantidade'
]
