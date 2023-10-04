"""
# api.user

This module contains the class User, used for manipulate
the users data stored on the database
"""

from api.connector import Connector, firestore_async

class User:
    """
    # api.user.User
    
    This class abstracts the "leitores" collection.
    \n
    Creates documents and make querys to the collection.
    """
    fields = ['data_nascimento', 'CEP', 'tel_pessoal', 'tel_profissional', 'escola', 'curso_serie', 'profissao', 'local_nascimento', 'nome', 'RG', 'residencia', 'email']
    __users = None
    @Connector.catch_error
    async def get_users() -> dict:
        """
        This function is for intern using. It loads all users data and save it into the User.__users variable.
        """
        if User.__users == None:
            User.__users = {user.id: user.to_dict() async for user in Connector.USERS.stream()}
        return User.__users
    
    @Connector.catch_error
    async def query(field: str="", op_string: str="", value: str="", to_dict: bool=False) ->  dict:
        """
        Makes queries to "leitores" collection.
        """
        await User.get_users()
        result = []
        try:    
            exec(f'''
for RG, user in User.__users.items():
    if not (str(user['{field}']) {op_string} '{value}'):
        continue
    result.append(user if to_dict else UserReference(**user))
''')
        except KeyError as e:
            return Connector.message('Field not found')
        return result if len(result) != 1 else result[0]   
    
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
        User.__users[RG] = user_data
        return user_data
    
    @Connector.catch_error   
    async def update(RG, **kwargs) -> None:
        """
        Updates an user in the database
        """
        await Connector.USERS.document(RG).update(kwargs)
        await User.get_users()
        User.__users[RG].update(kwargs)
        
    @Connector.catch_error   
    async def favorite(RG, book_id) -> None:
        """
        Favorites a book
        """
        await User.get_users()
        favorite = User.__users[RG]['favoritos']
        if book_id in favorite:
            await Connector.USERS.document(RG).update({
                'favoritos': firestore_async.firestore.ArrayRemove([book_id])
            })
            User.__users[RG]['favoritos'].pop(favorite.index(book_id))
        else:
            await Connector.USERS.document(RG).update({
                'favoritos': firestore_async.firestore.ArrayUnion([book_id])
            })
            User.__users[RG]['favoritos'].append(book_id)
    
    @Connector.catch_error
    async def delete(RG) -> None:
        """
        Deletes a user firestore document
        """
        await Connector.USERS.document(RG).delete()
        await User.get_users()
        User.__users.pop(RG, '')
