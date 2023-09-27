"""
# api.user

This module contains an ORM implementation for the firestore_async module for manipulate
the users data stored on the database
"""

from api.connector import Connector

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
    
    def to_dict(self) -> dict:
        """
        Returns dict version of the database data
        """
        return {attr: getattr(self, attr) for attr in self.fields}
    
    @Connector.catch_error   
    async def save(self) -> None:
        """
        Saves the changes on the database
        """
        await Connector.USERS.document(self.RG).update(self.to_dict())
    
    @Connector.catch_error
    async def delete(self) -> None:
        """
        Deletes UserReference instance and the corresponding firestore document
        """
        await Connector.USERS.document(self.RG).delete()
        del self

class User:
    """
    # api.user.User
    
    This class abstracts the "leitores" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    @Connector.catch_error
    async def query(field_path: str="", op_string: str="", value: str="", only_ids: bool=False) -> dict:
        """
        Makes queries to "leitores" collection.
        \n
        If field_path, op_string and value equals to "" then returns all the documents
        on collection.
        """
        result = []
        #if all the str args are not ""
        if all([field_path, op_string, value]):
            async for user in Connector.USERS.where(filter=Connector.field_filter(field_path, op_string, value)).stream():
                result.append(user.id if only_ids else user.to_dict())
        else:
            async for user in Connector.USERS.stream():
                result.append(user.id if only_ids else user.to_dict())
        return None if result == [] else result     
    
    @Connector.catch_error
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
    ) -> UserReference | dict:
        """
        This function creates a new document on the 'leitores' collection and returns a 
        UserReference object pointing to.
        \n
        If the user already exists, then returns a dict with a message about this
        """
        
        #If user already exists
        if RG in await User.query(only_ids=True): 
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
        return UserReference(**user_data)
