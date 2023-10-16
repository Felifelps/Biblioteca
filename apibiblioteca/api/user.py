"""
# api.user

This module contains an ORM implementation for the firestore_async module for manipulate
the users data stored on the database
"""

from .connector import Connector

class UserReference:
    """
    # api.user.UserReference
    
    This class abstracts a firestore document set on the "leitores" collection. 
    \n 
    When instantiated, it gets the values from the database and stores it in attributes 
    with the same name of the fields. 
    \n
    After changes, the save method sends the values to 
    the database.
    """
    
    def __init__(self, **kwargs):
        """
        Converts kwargs argument into attrs and saves kwargs keys in the fields attribute
        """
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def __str__(self) -> str:
        return f'<UserReference(RG="{self.RG}", nome="{self.nome}")>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __setitem__(self, name, value) -> None:
        '''
        This function transforms user[name] = value in user.name = value
        '''
        setattr(self, name, value)
        
    def __getitem__(self, name):
        '''
        This function returns user.name
        '''
        if hasattr(self, name):
            return getattr(self, name)
        return None
    
    def to_dict(self) -> dict:
        """
        Returns dict version of the database data
        """
        return {attr: getattr(self, attr) for attr in self.fields}
       
    async def save(self) -> None:
        """
        Saves the changes on the database
        """
        await Connector.USERS.document(self.RG).update(self.to_dict())
        User._users[self.RG] = self.to_dict()
    
    async def delete(self) -> None:
        """
        Deletes UserReference instance and the corresponding firestore document
        """
        await Connector.USERS.document(self.RG).delete()
        User._users.pop(self.RG, '')
        del self

class User:
    """
    # api.user.User
    
    This class abstracts the "leitores" collection.
    \n
    Creates documents and make querys to the collection.
    """
    _users = None
    
    async def get_users() -> dict:
        """
        It loads all users data and save it into the User._users variable, if it is None.
        """
        if User._users == None:
            User._users = {user.id: user.to_dict() async for user in Connector.USERS.stream()}
        return User._users
    
    async def all() -> list:
        """
        Returns all users of database
        """
        await User.get_users()
        return [UserReference(**user) for RG, user in User._users.items()]
    
    async def query(field: str="", op_string: str="", value: str="", to_dict: bool=False) -> dict:
        """
        Makes queries to "leitores" collection.
        """
        result = []
        users = await User.get_users()
        try:    
            exec(f'''
for RG, user in users.items():
    if not (str(user['{field}']) {op_string} '{value}'):
        continue
    result.append(user if to_dict else UserReference(**user))
''')
        except KeyError as e:
            return Connector.message('Field not found')
        return result if len(result) != 1 else result[0]   
    
    async def get(RG: str, default=None, to_dict: bool=True) -> dict:
        '''
        Returns user data from the database in the shape of a dict if to_dict == True, else UserReference. If not found, returns default.
        '''
        if RG in (await User.get_users()).keys():
            return User._users[RG] if to_dict else UserReference(**User._users[RG])
        return default 
    
    async def new( 
        RG: str,
        nome: str,
        data_nascimento: str,
        local_nascimento: str,
        email: str,
        CEP: str,
        tel_pessoal: str,
        residencia: str,
        profissao: str="",
        tel_profissional: str="",
        escola: str="",
        curso_serie: str="",
        **kwargs
    ) -> dict:
        """
        This function creates a new document on the 'leitores' collection and returns a 
        UserReference object pointing to.
        \n
        If the user already exists, then returns a dict with a message about this
        """
        #If user already exists
        if RG in await User.get_users(): 
            return Connector.message('Usuário já existente')
        user_data = {
            'RG': RG,
            'nome': nome,
            'data_nascimento': data_nascimento,
            'local_nascimento': local_nascimento,
            'email': email,
            'CEP': CEP,
            'tel_pessoal': tel_pessoal,
            'residencia': residencia,
            'profissao': profissao,
            'tel_profissional': tel_profissional,
            'escola': escola,
            'curso_serie': curso_serie,
            'data_cadastro': Connector.today(),
            'valido': False,
            'favoritos': [],
            'livro': False     
        }
        await Connector.USERS.document(RG).set(user_data)
        User._users[RG] = user_data
        return user_data
