from api.connector import Connector

class Book:
    quantity = 0
    
    def book_exists(func):
        async def wrapper(*args, **kwargs):
            id, *_ = args
            if id not in await Book.all(): 
                return Connector.message('Livro não encontrado.')
            return await func(*args, **kwargs)
        return wrapper
        
    @Connector.catch_error
    async def all(only_ids=True):
        books = [book.id if only_ids else book.to_dict() async for book in Connector.BOOKS.stream()]
        Book.quantity = len(books)
        return books
        
    @Connector.catch_error
    async def get(id):
        async for book in Connector.BOOKS.where(filter=Connector.field_filter('id', '==', id)).stream():
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
        prateleira
    ):
        print(Book.quantity)
        id = Book.quantity + 1
        book_data = {
            'id': id,
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
            await Connector.BOOKS.document(id).set(book_data)
            Book.quantity = id
            return book_data
        except Exception as e:
            return Connector.message('Um erro ocorreu', str(e))
    
    @Connector.catch_error
    @book_exists
    async def update(id, **kwargs):
        await Connector.BOOKS.document(id).update(kwargs)
        return Connector.message('Livro atualizado.')
    
    @Connector.catch_error
    @book_exists
    async def delete(id):
        await Connector.BOOKS.document(id).delete()
        return Connector.message('Livro excluído.')
    
    @Connector.catch_error
    @book_exists
    async def validate(id):
        await Connector.BOOKS.document(id).update({'valido': True})
        return Connector.message('Livro validado.')
        