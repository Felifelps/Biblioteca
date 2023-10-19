"""
# api.user

This module contains an ORM implementation for the firestore_module for manipulate
the users data stored on the database
"""
from .data import DATA
from .utils import today

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
    
    def save(self) -> None:
        """
        Saves the changes on the database
        """
        DATA.update('users', {self.RG: self.to_dict()})
    
    def delete(self) -> None:
        """
        Deletes UserReference instance and the corresponding firestore document
        """
        data = DATA.data
        data['users'].pop(self.RG)
        DATA.change(data)
        del self

class User:
    """
    # api.user.User
    
    This class abstracts the "leitores" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    def get_users(to_dict=True) -> dict:
        return DATA.data.get('users') if to_dict else [UserReference(user) for user in DATA.data.get('users').values()]
    
    def query(field: str="", op_string: str="", value: str="", to_dict: bool=True) -> dict:
        """
        Makes queries to "leitores" collection.
        """
        result = []
        users = DATA.data.get('users')
        try:    
            exec(f'''
for RG, user in users.items():
    if not (str(user['{field}']) {op_string} '{value}'):
        continue
    result.append(user if to_dict else UserReference(**user))
''')
        except KeyError as e:
            raise 'Field not found'
        return result if len(result) != 1 else result[0]   
    
    def get(RG, default=None, to_dict=True):
        user = DATA.data.get('users').get(RG, default)
        if user == default or to_dict:
            return user
        return UserReference(**user)
    
    def new( 
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
        to_dict=True
    ) -> dict:
        """
        This function creates a new document on the 'leitores' collection and returns a 
        UserReference object pointing to.
        \n
        If the user already exists, then returns a dict with a message about this
        """
        #If user already exists
        if RG in DATA.data.get('users'): 
            return False
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
            'data_cadastro': today(),
            'valido': False,
            'favoritos': [],
            'livro': False     
        }
        DATA.update('users', {RG: user_data})
        return user_data if to_dict else UserReference(**user_data)