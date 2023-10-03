"""
# api.lending

This module contains an ORM implementation for the firestore_async module for manipulate
the lendings data stored on the database
"""

from api.connector import Connector
    
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
        
    def __str__(self) -> str:
        return f'<LendingReference(id={self.id}, livro="{self.livro}", leitor="{self.leitor}")>'
    
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
        await Connector.LENDINGS.document(self.id).update(self.to_dict())
        Lending.lendings[self.id] = self.to_dict()
    
    @Connector.catch_error
    async def delete(self) -> None:
        """
        Deletes LendingReference instance and the corresponding firestore document
        """
        await Connector.LENDINGS.document(self.id).delete()
        Lending.lendings.pop(self.id, '')
        del self

class Lending:
    """
    # api.lending.Lending
    
    This class abstracts the "emprestimos" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    quantity = None
    lendings = None
    @Connector.catch_error
    async def __load_lendings() -> None:
        """
        This function is for intern using. It loads all lendings data and save it into the Lending.lendings variable.
        """
        if Lending.lendings == None:
            Lending.lendings = {lending.id: lending.to_dict() async for lending in Connector.LENDINGS.stream()}
            Lending.quantity = len(Lending.lendings)
    
    @Connector.catch_error
    async def all() -> list[LendingReference]:
        """
        Returns all lendings of database
        """
        await Lending.__load_lendings()
        return [LendingReference(**lending) for RG, lending in Lending.lendings.items()]
    
    @Connector.catch_error
    async def query(field: str, op_string: str, value: str, to_dict: bool=False) -> LendingReference | dict:
        """
        Makes queries to "emprestimos" collection.
        """

        await Lending.__load_lendings()
        result = []
        try:
            exec(f'''
for id, lending in Lending.lendings.items():
    if not (str(lending['{field}']) {op_string} '{value}'):
        continue
    result.append(lending if to_dict else LendingReference(**lending))
''')
        except KeyError as e:
            return Connector.message('Field not found')
        return result if len(result) != 1 else result[0]    
    
    async def new(RG: str, lending_id: str) -> LendingReference:
        """
        This function creates a new document on the 'emprestimos' collection and returns a 
        LendingReference object pointing to.
        """
        if Lending.lendings == None:
            await Lending.__load_lendings()
            
        id = Lending.quantity + 1
        lending_data = {
            'id': str(id),
            'leitor': RG,
            'livro': lending_id,
            'multa': 0,
            'data_emprestimo': Connector.today(),
            'renovado': False,
            'data_finalizacao': False
        }
        await Connector.LENDINGS.document(str(id)).set(lending_data)
        Lending.quantity += 1
        Lending.lendings[str(id)] = lending_data
        return LendingReference(**lending_data)
