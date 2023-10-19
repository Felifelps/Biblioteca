"""
# api.lending

This module contains an ORM implementation for the firestore_module for manipulate
the lendings data stored on the database
"""

from .data import DATA
from .utils import today
    
class LendingReference:
    """
    # api.lending.LendingReference
    
    This class abstracts a firestore document set on the "emprestimos" collection. 
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
        This function transforms lending[name] = value in lending.name = value
        '''
        setattr(self, name, value)
        
    def __getitem__(self, name):
        '''
        This function returns lending.name
        '''
        if hasattr(self, name):
            return getattr(self, name)
        return None
    
    def __str__(self) -> str:
        return f'<LendingReference(id={self.id}, livro="{self.livro}", leitor="{self.leitor}")>'
    
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
        DATA.update('lendings', {self.id: self.to_dict()})
    
    def delete(self) -> None:
        """
        Deletes LendingReference instance and the corresponding firestore document
        """
        data = DATA.data
        data['lendings'].pop(self.id)
        DATA.change(data)
        del self

class Lending:
    """
    # api.lending.Lending
    
    This class abstracts the "emprestimos" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    def get_lendings(to_dict=True) -> dict:
        return DATA.data.get('lendings') if to_dict else [LendingReference(lending) for lending in DATA.data.get('lendings').values()]
    
    def query(field: str="", op_string: str="", value: str="", to_dict: bool=True) -> dict:
        """
        Makes queries to "leitores" collection.
        """
        result = []
        lendings = DATA.data.get('lendings')
        try:    
            exec(f'''
for id, lending in lendings.items():
    if not (str(lending['{field}']) {op_string} '{value}'):
        continue
    result.append(lending if to_dict else LendingReference(**lending))
''')
        except KeyError as e:
            raise 'Field not found'
        return result if len(result) != 1 else result[0]   
    
    def get(id, default=None, to_dict=True):
        lending = DATA.data.get('lendings').get(id, default)
        if lending == default or to_dict:
            return lending
        return LendingReference(**lending)  
    
    def new(RG: str, lending_id: str, to_dict=True) -> LendingReference:
        """
        This function creates a new document on the 'emprestimos' collection and returns a 
        LendingReference object pointing to.
        """
            
        id = len(DATA.data.get('lendings'))
        lending_data = {
            'id': str(id),
            'leitor': RG,
            'livro': lending_id,
            'multa': 0,
            'data_emprestimo': today(),
            'renovado': False,
            'data_finalizacao': False
        }
        DATA.update('lendings', {id, lending_data})
        return lending_data if to_dict else LendingReference(**lending_data)
