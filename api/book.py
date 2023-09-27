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
    
    @Connector.catch_error
    async def delete(self) -> None:
        """
        Deletes BookReference instance and the corresponding firestore document
        """
        await Connector.BOOKS.document(self.id).delete()
        del self

class Book:
    """
    # api.book.Book
    
    This class abstracts the "livros" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    quantity = None
    @Connector.catch_error
    async def query(field_path: str="", op_string: str="", value: str="", only_ids: bool=False) -> dict:
        """
        Makes queries to "livros" collection.
        \n
        If field_path, op_string and value equals to "" then returns all the documents
        on collection.
        """
        result = []
        #if all the str args are not ""
        if all([field_path, op_string, value]):
            async for book in Connector.BOOKS.where(filter=Connector.field_filter(field_path, op_string, value)).stream():
                result.append(book.id if only_ids else book.to_dict())
        else:
            async for book in Connector.BOOKS.stream():
                result.append(book.id if only_ids else book.to_dict())
        return None if result == [] else result    
    
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