from api.connector import Connector

class Book:
    quantity = None
    def book_exists(func):
        async def wrapper(*args, **kwargs):
            book = await Book.get(args[0])
            if 'message' in book.keys(): 
                return book
            return await func(*args, **kwargs)
        return wrapper
        
    @Connector.catch_error
    async def all(only_ids=True):
        return [book.id if only_ids else book.to_dict() async for book in Connector.BOOKS.stream()]
        
    @Connector.catch_error
    async def get(id):
        async for book in Connector.BOOKS.where(filter=Connector.field_filter('id', '==', str(id))).stream():
            return book.to_dict()
        return Connector.message('Livro não encontrado.')
    
    @Connector.catch_error
    async def new( 
        titulo,
        autor,
        editora,
        edicao,
        CDD,
        assuntos,
        estante,
        prateleira,
        **kwargs
    ):
        if Book.quantity == None: Book.quantity = len(await Book.all())
        id = Book.quantity + 1
        book_data = {
            'id': str(id),
            'titulo': titulo,
            'autor': autor,
            'editora': editora,
            'edicao': edicao,
            'CDD': CDD,
            'assuntos': assuntos,
            'estante': estante,
            'prateleira': prateleira,
            'leitor': False     
        }
        await Connector.BOOKS.document(str(id)).set(book_data)
        Book.quantity = id
        return book_data
    
    @Connector.catch_error
    @book_exists
    async def update(id, **kwargs):
        await Connector.BOOKS.document(str(id)).update(kwargs)
        return Connector.message('Livro atualizado.')
    
    @Connector.catch_error
    @book_exists
    async def delete(id):
        await Connector.BOOKS.document(str(id)).delete()
        return Connector.message('Livro excluído.')