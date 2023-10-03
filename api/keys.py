"""
# api.keys

This module contains the methods and a class to handle the api keys.
"""

from api.connector import Connector
from bcrypt import checkpw, gensalt, hashpw
from secrets import token_hex

class Keys:
    """
    # api.keys.Keys
    
    This class abstracts the "keys" collection of the database.
    """
    
    keys = None
    @Connector.catch_error
    async def get_keys() -> dict:
        """
        This function is for intern using. It loads all keys data and save it into the Keys.keys variable.
        """
        if Keys.keys == None:
            Keys.keys = {key.id: key.to_dict() async for key in Connector.API_KEYS.stream()}
        return Keys.keys
    
    def encrypt_key(key: str) -> list[bytes]:
        """
        Generate a salt and encrypt the given key, returning a list [encrypted_key, salt].
        """
        salt = gensalt()
        return [hashpw(bytes(key, encoding='utf-8'), salt), salt]
    
    @Connector.catch_error
    async def check_key(email: str, key: str) -> bool:
        """
        Checks if the given key corresponds to the given email api key.
        """
        await Keys.get_keys()
        return checkpw(bytes(key, encoding='utf-8'), Keys.keys[email]['encrypted_key'])
    
    @Connector.catch_error
    async def register_new_key(email: str, length: int=32) -> str | dict:
        """
        Registers and creates a new not validated api key in the database.
        """
        
        #if email already registered
        if email in await Keys.get_keys():
            return Connector.message('Email already registered')
        key = token_hex(length//2)
        data = Keys.encrypt_key(key)
        key_data = {
            "email": email,
            "encrypted_key": str(data[0]),
            "salt": str(data[1])
        }
        await Connector.API_KEYS.document(email).set(key_data)
        Keys.keys[email] = key_data
        return key
    
    @Connector.catch_error
    async def get(email: str) -> dict | str:
        """
        Gets an api key from the database.
        """
        return (await Keys.get_keys()).get(email, Connector.message('Email not found'))
        
    @Connector.catch_error
    async def delete(email: str) -> None:
        """
        Deletes an api key.
        """
        await Keys.get_keys()
        await Connector.API_KEYS.document(email).delete()
        Keys.keys.pop(email, '')