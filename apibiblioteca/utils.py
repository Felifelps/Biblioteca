"""This module contains various utility functions for working
with a Firestore database.

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

from os import environ
import unicodedata
from bcrypt import checkpw
from dotenv import load_dotenv
from firebase_admin import (
    credentials,
    firestore,
    initialize_app
)


# Load environment variables
load_dotenv()

# Extract and format Firebase credentials from environment variables
cred = {}
for key, value in environ.items():
    if 'FIREBASE' in key:
        cred[key.replace('FIREBASE_', '').lower()] = value.replace('\\n', '\n')

private_key = [cred.pop(f'private_key_n_{i}') for i in range(28)]
cred['private_key'] = '\n'.join(private_key)

# Initialize Firestore database
initialize_app(credentials.Certificate(cred))
DB = firestore.client()


def check_admin_login(login: str) -> bool:
    """Check if the given login matches the admin login."""
    return checkpw(
        bytes(login, encoding='utf-8'),
        bytes(environ.get('ADMIN_LOGIN'), encoding='utf-8')
    )


def check_admin_password(password: str) -> bool:
    """Check if the given password matches the admin password."""
    return checkpw(
        bytes(password, encoding='utf-8'),
        bytes(environ.get('ADMIN_PASSWORD'), encoding='utf-8')
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
