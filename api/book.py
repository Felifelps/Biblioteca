"""
# api.book

This module contains an ORM implementation for the firestore_async module for manipulate
the books data stored on the database
"""

from api.connector import Connector

class BookReference:
    """
    # api.book.BookReference
    
    This class abstracts a firestore document set on the "livros" collection. 
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
        return f'<BookReference(id={self.id}, titulo="{self.titulo}")>'
    
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
        await Connector.BOOKS.document(self.id).update(self.to_dict())
        Book.books[self.id] = self.to_dict()
    
    @Connector.catch_error
    async def delete(self) -> None:
        """
        Deletes BookReference instance and the corresponding firestore document
        """
        await Connector.BOOKS.document(self.id).delete()
        Book.books.pop(self.id)
        del self

class Book:
    """
    # api.book.Book
    
    This class abstracts the "livros" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    quantity = None
    books = None
    @Connector.catch_error
    async def __load_books() -> None:
        """
        This function is for intern using. It loads all books data and save it into the Book.books variable.
        """
        if Book.books == None:
            Book.books = {book.id: book.to_dict() async for book in Connector.BOOKS.stream()}
        Book.quantity = len(Book.books)
    
    @Connector.catch_error
    async def all() -> list[BookReference]:
        """
        Returns all books of database
        """
        await Book.__load_books()
        return [BookReference(**book) for RG, book in Book.books.items()]
    
    @Connector.catch_error
    async def query(field: str, op_string: str, value: str, to_dict: bool=False) -> BookReference | dict:
        """
        Makes queries to "livros" collection.
        """
        
        await Book.__load_books()
        result = []
        try:
            exec(f'''
for id, book in Book.books.items():
    if not (str(book['{field}']) {op_string} '{value}'):
        continue
    result.append(book if to_dict else BookReference(**book))
''')
        except KeyError as e:
            return Connector.message('Field not found')
        return result if len(result) != 1 else result[0]       
    
    @Connector.catch_error
    async def new( 
        titulo: str,
        autor: str,
        editora: str,
        edicao: str,
        CDD: str,
        assuntos: str,
        estante: str,
        prateleira: str,
        **kwargs
    ) -> BookReference | dict:
        """
        This function creates a new document on the 'livros' collection and returns a 
        BookReference object pointing to.
        """
        await Book.__load_books()
        
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
        Book.quantity += 1
        Book.books[str(id)] = book_data
        return BookReference(**book_data)