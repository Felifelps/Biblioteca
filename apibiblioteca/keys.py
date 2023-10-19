"""
# api.keys

This module contains the methods and a class to handle the api keys.
"""
from asyncio import to_thread
from bcrypt import checkpw, gensalt, hashpw
from .data import DATA
from secrets import token_hex

class Keys:
    """
    # api.keys.Keys
    
    This class abstracts the "keys" collection of the database.
    """
    def get_keys():
        return DATA['keys']
    
    def encrypt_key(key: str) -> list:
        """
        Generate a salt and encrypt the given key, returning a list [encrypted_key, salt].
        """
        salt = gensalt()
        return [hashpw(bytes(key, encoding='utf-8'), salt), salt]
    
    def check_key(email: str, key: str) -> bool:
        """
        Checks if the given key corresponds to a given email api key.
        """
        return checkpw(bytes(key, encoding='utf-8'), DATA['keys'][email]['encrypted_key'])
    
    def get_email_from_key(key: str, default=None) -> str:
        """
        Gets an email by its associated key. If not found, returns None.
        """
        for value in DATA['keys'].values():
            if checkpw(bytes(key, encoding='utf-8'), bytes(value['encrypted_key'][2:-1], encoding='utf-8')):
                return value['email']
        return default
    
    def register_new_key(email: str, length: int=32):
        """
        Registers and creates a new not validated api key in the database.
        """
        
        #if email already registered
        if email in DATA['keys']:
            return None
        key = token_hex(length//2)
        data = Keys.encrypt_key(key)
        key_data = {
            "email": email,
            "encrypted_key": str(data[0]),
            "salt": str(data[1])
        }
        DATA['keys'].update({email: key_data})
        return key
    
    def get(email: str, default=None) -> str:
        """
        Gets an api key from the database.
        """
        return DATA['keys'].get(email, default)
    
    def delete(email: str) -> None:
        """
        Deletes an api key.
        """
        DATA['keys'].pop(email)