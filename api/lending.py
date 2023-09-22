from api.book import Book
from api.connector import Connector, firestore_async
from api.user import User

from datetime import datetime

class Lending:
    quantity = None
    
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
    async def new(RG):
        user_data = await User.get(RG)
        if 'message' in user_data.keys(): 
            return user_data
        elif not user_data['livro']:
            return Connector.message('O usuário não reservou um livro.')
        
        book_data = await Book.get(user_data['livro'])
        if 'message' in book_data.keys():
            return book_data
        
        if Lending.quantity == None: 
            Lending.quantity = len(await Lending.all())
            
        id = Lending.quantity + 1
        lend_data = {
            'id': str(id),
            'leitor': RG,
            'livro': user_data['livro'],
            'multa': 0,
            'data_emprestimo': Connector.today(),
            'renovado': False,
            'data_finalizacao': False
        }
        await Connector.LENDINGS.document(str(id)).set(lend_data)
        Lending.quantity += 1
        return lend_data
    
    @Connector.catch_error
    async def update(id, **kwargs):
        await Connector.LENDINGS.document(str(id)).update(kwargs)
        return Connector.message('Empréstimo alterado.')
    
    @Connector.catch_error
    async def delete(id):
        await Connector.LENDINGS.document(str(id)).delete()
        return Connector.message('Empréstimo alterado.')
    
    @Connector.catch_error
    async def finalize(id):
        lending_data = await Lending.get(id)
        if 'message' in lending_data.keys():
            return lending_data
        elif lending_data['data_finalizacao']:
            return Connector.message('Empréstimo ja finalizado.')
        await Lending.update(
            id, 
            data_finalizacao=Connector.today()
        )
        await User.cancel_reserve(lending_data['leitor'])
        return Connector.message('Empréstimo finalizado.')

    @Connector.catch_error
    async def p():
        pass
    
    @Connector.catch_error
    async def check_lending(id):
        lending = await Lending.get(id)
        data_emprestimo = datetime.strptime(lending['data_emprestimo'], '%d/%m/%y às %H:%M:%S')
        
        if not lending['pego'] and (datetime.today() - data_emprestimo).days > 2:
            Lending.finalize(id)
            return Connector.message('O usuário reservou o livro e não foi buscá-lo. Reserva cancelada.')
        elif not lending['renovado'] and (datetime.today() - data_emprestimo).days > 12:
            pass
        
    


        