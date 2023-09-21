from api.book import Book
from api.connector import Connector, firestore_async
from api.user import User

from datetime import datetime

class Lending:
    quantity = None
    
    def today():
        return datetime.today().strftime('%d/%m/%y às %H:%M:%S')
    
    def lending_exists(func):
        async def wrapper(*args, **kwargs):
            lending = await Lending.get(args[0])
            if 'message' in lending.keys():
                return lending
            return await func(*args, **kwargs)
        return wrapper
    
    @Connector.catch_error
    async def all(only_ids=True):
        return [lending.id if only_ids else lending.to_dict() async for lending in Connector.LENDINGS.stream()]
        
    @Connector.catch_error
    async def get(id):
        async for lending in Connector.LENDINGS.where(filter=Connector.field_filter('id', '==', str(id))).stream():
            return lending.to_dict()
        return Connector.message('Empréstimo não encontrado.')
    
    @Connector.catch_error
    @firestore_async.firestore.async_transactional
    async def new(RG, book_id):
        user = await User.get(RG)
        if 'message' in user.keys(): 
            return user
        elif user['livro'] != False:
            return Connector.message('Usuário já reservou um livro.')
        
        book = await Book.get(book_id)
        if 'message' in book:
            return book
        elif book['leitor'] != False:
            return Connector.message('Livro já reservado.')
        
        if Lending.quantity == None: 
            Lending.quantity = len(await Lending.all())
            
        id = Lending.quantity + 1
        lend_data = {
            'id': id,
            'leitor': RG,
            'livro': book_id,
            'data_emprestimo': Lending.today(),
            'multa': 0,
            'pego': False,
            'renovado': False,
            'data_finalizacao': False
        }
        await Connector.LENDINGS.document(str(id)).set(lend_data)
        await Book.update(book_id, leitor=RG)
        await User.update(RG, livro=book_id)
        Lending.quantity += 1
        return lend_data
    
    @Connector.catch_error
    async def update(id, **kwargs):
        await Connector.LENDINGS.document(str(id)).update(kwargs)
        return Connector.message('Empréstimo alterado.')
    
    @Connector.catch_error
    async def check_lending(id):
        lending = await Lending.get(id)
        data_emprestimo = datetime.strptime(lending['data_emprestimo'], '%d/%m/%y às %H:%M:%S')
        
        if lending['pego'] == False and (datetime.today() - data_emprestimo).days > 2:
            await Lending.update(
                id, 
                finalizado=True, 
                data_finalizacao=Lending.today()
            )
            return Connector.message('O usuário reservou o livro e não foi buscá-lo. Reserva cancelada.')

        
    


        