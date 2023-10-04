"""
# api.book

This module contains a class used for manipulate
the books data stored on the database
"""

from api.connector import Connector

class Book:
    """
    # api.book.Book
    
    This class abstracts the "livros" collection.
    \n
    Creates documents and make querys to the collection.
    """
    fields = ['titulo', 'autor', 'editora', 'edicao', 'CDD', 'assuntos', 'estante', 'prateleira', 'leitor']
    quantity = None
    __books = None
    @Connector.catch_error
    async def get_books() -> None:
        """
        This function is for intern using. It loads all books data and save it into the Book.__books variable.
        """
        if Book.__books == None:
            Book.__books = {book.id: book.to_dict() async for book in Connector.BOOKS.stream()}
        Book.quantity = len(Book.__books)
        return Book.__books
    
    @Connector.catch_error
    async def all() -> list[dict]:
        """
        Returns all books of database
        """
        await Book.get_books()
        return [book for RG, book in Book.__books.items()]
    
    @Connector.catch_error
    async def query(field: str, op_string: str, value: str, to_dict: bool=False) -> dict:
        """
        Makes queries to "livros" collection.
        """
        
        await Book.get_books()
        result = []
        try:
            exec(f'''
for id, book in Book.__books.items():
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
    ) -> dict:
        """
        This function creates a new document on the 'livros' collection and returns a 
        BookReference object pointing to.
        """
        await Book.get_books()
        
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
        print(list(book_data.keys()))
        await Connector.BOOKS.document(str(id)).set(book_data)
        Book.quantity += 1
        Book.__books[str(id)] = book_data
        return book_data
    
    @Connector.catch_error   
    async def update(book_id, **kwargs) -> None:
        """
        Updates a book in the database
        """
        await Connector.BOOKS.document(book_id).update(kwargs)
        await Book.get_books()
        Book.__books[book_id].update(kwargs)
    
    @Connector.catch_error
    async def delete(book_id) -> None:
        """
        Deletes a book in the database
        """
        await Connector.BOOKS.document(book_id).delete()
        await Book.get_books()
        Book.__books.pop(book_id, '')