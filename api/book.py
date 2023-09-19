from api.connector import Connector

class Book(Connector):
    async def __init__(self):
        self.id = 0
        print(self.BOOKS.count().stream())
    
    async def new_book(
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
        if await self.get_book(self.id) == None: return False
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
        await self.BOOKS.document(self.id).set(book_data)
        return book_data
    
    async def update_book(self, RG, *kwargs):
        await self.bookS.document(RG).update(kwargs)
        
    async def delete_book(self, RG):
        await self.bookS.document(RG).delete()
    
    async def get_books(self, only_ids=True):
        return [book.id if only_ids else book.to_dict() async for book in self.bookS.stream()]
    
    async def get_book(self, RG):
        for book in await self.get_books(False):
            if book['RG'] == RG: return book
        return False
    
    async def validate_book(self, RG):
        await self.bookS.document(RG).update({
            'valido': True
        })
        