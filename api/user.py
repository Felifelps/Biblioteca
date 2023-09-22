from api.connector import Connector, firestore_async
from api.book import Book
from api.email import Email
import datetime

class User:
    def user_exists(func):
        async def wrapper(*args, **kwargs):
            user = await User.get(args[0])
            if 'message' in user.keys(): 
                return user
            return await func(*args, **kwargs)
        return wrapper
    
    @Connector.catch_error
    async def all(only_ids=True):
        return [user.id if only_ids else user.to_dict() async for user in Connector.USERS.stream()]
    
    @Connector.catch_error
    async def get(RG):
        async for user in Connector.USERS.where(filter=Connector.field_filter('RG', '==', RG)).stream():
            return user.to_dict()
        return Connector.message('Usuário não encontrado.')
    
    @Connector.catch_error
    async def new( 
        RG,
        nome,
        data_nascimento,
        local_nascimento,
        email,
        CEP,
        tel_pessoal,
        residencia,
        profissao="",
        tel_profissional="",
        escola="",
        curso_serie="",
        **kwargs
    ):
        if RG in await User.all(): 
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
        return user_data
    
    @Connector.catch_error
    @user_exists
    async def update(RG, **kwargs):
        await Connector.USERS.document(RG).update(kwargs)
        return Connector.message('Usuário atualizado.')
    
    @Connector.catch_error
    @user_exists
    async def delete(RG):
        await Connector.USERS.document(RG).delete()
        return Connector.message('Usuário excluído.')
    
    async def __favorite(RG, book_id, favorite=True):
        operation = firestore_async.firestore.ArrayUnion if favorite else firestore_async.firestore.ArrayRemove
        await User.update(RG, favoritos=operation([book_id]))
        return Connector.message(f'Livro {"" if favorite else "des"}favoritado.')
    
    async def favorite(RG, book_id):
        return await User.__favorite(RG, book_id)
        
    async def unfavorite(RG, book_id):
        return await User.__favorite(RG, book_id, False)
    
    async def validate(RG):
        await User.update(RG, valido=True)
        return Connector.message('Usuário validado.')
    
    @Connector.catch_error
    @user_exists
    async def reserve(RG, book_id):
        user_data = await User.get(RG)
        if user_data['livro']:
            return Connector.message('O usuário já reservou um livro.')
        await User.update(RG, livro=book_id)
        await Book.reserve(book_id, RG)
        return Connector.message('Livro reservado.')
    
    @Connector.catch_error
    @user_exists
    async def cancel_reserve(RG):
        user_data = await User.get(RG)
        if not user_data['livro']:
            return Connector.message('O usuário jnão reservou um livro.')
        await Book.give_back(user_data['livro'])
        await User.update(RG, livro=False)
        return Connector.message('Reserva cancelada.')
        
    