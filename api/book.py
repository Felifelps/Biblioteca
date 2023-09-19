from api.connector import Connector

class Book(Connector):
    def book_exists(exists=True):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                self, RG = args[0], args[1]
                if 'message' in await self.get(RG) == exists: 
                    return self.error('Livro não encontrado.')
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def all(self, only_ids=True):
        return [i.id if only_ids else i.to_dict() async for i in self.bookS.stream()]
    
    async def get(self, RG):
        try:
            async for book in self.bookS.where(filter=self.field_filter('RG', '==', RG)).stream():
                return book.to_dict()
            return self.error('Livro não encontrado.')
        except Exception as e:
            return self.error('Um erro ocorreu.', str(e))
    
    @book_exists(False)
    async def new(
        self,  
        titulo,
        autor,
        editora,
        edicao,
        CDD,
        assuntos,
        estante,
        prateleira
    ):
        book_data = {
            'id': self.id,
            'titulo': titulo,
            'autor': autor,
            'editora': editora,
            'edicao': edicao,
            'CDD': CDD,
            'assuntos': assuntos,
            'estante': estante,
            'prateleira': prateleira,
            'disponivel': True     
        }
        try:
            await self.bookS.document(RG).set(book_data)
            return book_data
        except Exception as e:
            return self.error('Um erro ocorreu', str(e))
    
    @book_exists()
    async def update(self, RG, **kwargs):
        try:
            await self.bookS.document(RG).update(kwargs)
        except Exception as e:
            return self.error('Não foi possível atualizar.', str(e))
    
    @book_exists()
    async def delete(self, RG):
        try:
            await self.bookS.document(RG).delete()
        except Exception as e:
            return self.error('Não foi possível excluir.', str(e))
    
    @book_exists()
    async def validate(self, RG):
        try:
            await self.bookS.document(RG).update({'valido': True})
        except Exception as e:
            return self.error('Não foi possível validar.', str(e))

        