from api.connector import Connector
from bcrypt import checkpw, gensalt, hashpw
from secrets import token_hex

class Keys:
    keys = None
    @Connector.catch_error
    async def __load_keys() -> dict:
        """
        This function is for intern using. It loads all keys data and save it into the Keys.keys variable.
        """
        if Keys.keys == None:
            Keys.keys = {key.id: key.to_dict() async for key in Connector.API_KEYS.stream()}
        return Keys.keys
    
    def encrypt_key(key):
        salt = gensalt()
        return [hashpw(bytes(key, encoding='utf-8'), salt), salt]
    
    def check_key(key, encrypted_key):
        return checkpw(bytes(key, encoding='utf-8'), encrypted_key)
    
    @Connector.catch_error
    async def register_new_key(email, length=32):
        if email in await Keys.__load_keys():
            return Connector.message('Email already registered')
        
        key = token_hex(length//2)
        data = Keys.encrypt_key(key)
        key_data = {
            "email": email,
            "encrypted_key": data[0],
            "salt": data[1],
            "validated": False
        }
        await Connector.API_KEYS.document(email).set(key_data)
        Keys.keys[email] = key_data
        return key_data
    
    @Connector.catch_error
    async def get(email):
        print(Keys.keys)
        return (await Keys.__load_keys()).get(email, Connector.message('Email not found'))
    
    @Connector.catch_error
    async def validate(email):
        await Keys.__load_keys()
        await Connector.API_KEYS.document(email).update({"validated": True})
        Keys.keys[email]['validated'] = True
        
    @Connector.catch_error
    async def delete(email):
        await Keys.__load_keys()
        await Connector.API_KEYS.document(email).delete()
        Keys.keys.pop(email)
