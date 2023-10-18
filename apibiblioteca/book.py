"""
# apibiblioteca.book

This module contains an ORM implementation for the firestore_module for manipulate
the books data stored on the database
"""
from asyncio import to_thread
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
    
    async def save(self) -> None:
        """
        Saves the changes on the database
        """
        await to_thread(DATA.update('books', {self.id: self.to_dict()}))
    
    async def delete(self) -> None:
        """
        Deletes BookReference instance and the corresponding firestore document
        """
        data = await to_thread(DATA.data)
        data['books'].pop(self.id)
        await to_thread(DATA.change(data))
        del self

class Book:
    """
    # apibiblioteca.book.Book
    
    This class abstracts the "livros" collection.
    \n
    Creates documents and make querys to the collection.
    """

    async def get_books(to_dict=True) -> dict:
        return (await to_thread(DATA.data))['books'] if to_dict else [BookReference(book) for book in (await to_thread(DATA.data))['books'].values()]
    
    async def query(field: str="", op_string: str="", value: str="", to_dict: bool=True) -> dict:
        """
        Makes queries to "leitores" collection.
        """
        result = []
        books = (await to_thread(DATA.data))['books']
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
    
    async def get(id, to_dict=True):
        book = (await to_thread(DATA.data))['books'].get(id, None)
        if not book or to_dict:
            return book
        return BookReference(**book)    
    
    async def new( 
        titulo: str,
        autor: str,
        editora: str,
        edicao: str,
        CDD: str,
        assuntos: str,
        estante: str,
        prateleira: str,
        to_dict=True
    ) -> dict:
        """
        This function creates a new document on the 'livros' collection and returns a 
        BookReference object pointing to.
        """
        
        id = len((await to_thread(DATA.data))['books'])
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
        await to_thread(DATA.update('books', {id, book_data}))
        return book_data if to_dict else BookReference(**book_data)