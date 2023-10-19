"""
# apibiblioteca.book

This module contains an ORM implementation for the firestore_module for manipulate
the books data stored on the database
"""
from .data import DATA

class BookReference:
    """
    # apibiblioteca.book.BookReference
    
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
        
    def __setitem__(self, name, value) -> None:
        '''
        This function transforms book[name] = value in book.name = value
        '''
        setattr(self, name, value)
        
    def __getitem__(self, name):
        '''
        This function returns book.name
        '''
        if hasattr(self, name):
            return getattr(self, name)
        return None
    
    def __str__(self) -> str:
        return f'<BookReference(id={self.id}, titulo="{self.titulo}")>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> dict:
        """
        Returns dict version of the database data
        """
        return {attr: getattr(self, attr) for attr in self.fields}
    
    def save(self) -> None:
        """
        Saves the changes on the database
        """
        DATA.update('books', {self.id: self.to_dict()})
    
    def delete(self) -> None:
        """
        Deletes BookReference instance and the corresponding firestore document
        """
        data = DATA.data
        data['books'].pop(self.id)
        DATA.change(data)
        del self

class Book:
    """
    # apibiblioteca.book.Book
    
    This class abstracts the "livros" collection.
    \n
    Creates documents and make querys to the collection.
    """

    def get_books(to_dict=True) -> dict:
        return DATA.data.get('books') if to_dict else [BookReference(book) for book in DATA.data.get('books').values()]
    
    def query(field: str="", op_string: str="", value: str="", to_dict: bool=True) -> dict:
        """
        Makes queries to "leitores" collection.
        """
        result = []
        books = DATA.data.get('books')
        try:    
            exec(f'''
for id, book in books.items():
    if not (str(book['{field}']) {op_string} '{value}'):
        continue
    result.append(book if to_dict else BookReference(**book))
''')
        except KeyError as e:
            raise 'Field not found'
        return result if len(result) != 1 else result[0]   
    
    def get(id, default=None, to_dict=True):
        book = DATA.data.get('books').get(id, default)
        if book == default or to_dict:
            return book
        return BookReference(**book)    
    
    def new( 
        titulo: str,
        autor: str,
        editora: str,
        edicao: str,
        CDD: str,
        assuntos: str,
        estante: str,
        prateleira: str,
        to_dict=True
    ):
        """
        This function creates a new document on the 'livros' collection and returns a 
        BookReference object pointing to.
        """
        
        id = len(DATA.data.get('books'))
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
        DATA.update('books', {id: book_data})
        return book_data if to_dict else BookReference(**book_data)