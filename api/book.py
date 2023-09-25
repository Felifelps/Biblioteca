from api.connector import Connector

class BookReference:
    def __init__(self, **kwargs):
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def __str__(self) -> str:
        return f'<BookReference(id={self.id}, titulo="{self.titulo}")>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.fields}
    
    @Connector.catch_error   
    async def save(self):
        await Connector.BOOKS.document(self.id).update(self.to_dict())
    
    @Connector.catch_error
    async def delete(self):
        await Connector.BOOKS.document(self.id).delete()
        del self

class Book:
    quantity = None
    @Connector.catch_error
    async def query(field_path="", op_string="", value="", only_ids=False):
        if not all([field_path, op_string, str(value)]):
            return [book.id if only_ids else BookReference(**book.to_dict()) async for book in Connector.BOOKS.stream()]
        return [book.id if only_ids else BookReference(**book.to_dict()) async for book in Connector.BOOKS.where(filter=Connector.field_filter(field_path, op_string, str(value))).stream()]        
    
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
        if Book.quantity == None: Book.quantity = len(await Book.query(only_ids=True))
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
        return BookReference(**book_data)