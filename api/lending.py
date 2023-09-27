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
    
    @Connector.catch_error
    async def delete(self) -> None:
        """
        Deletes LendingReference instance and the corresponding firestore document
        """
        await Connector.LENDINGS.document(self.id).delete()
        del self

class Lending:
    """
    # api.lending.Lending
    
    This class abstracts the "emprestimos" collection.
    \n
    Creates documents and make querys to the collection.
    """
    
    quantity = None
    @Connector.catch_error
    async def query(field_path: str="", op_string: str="", value: str="", only_ids: bool=False) -> dict:
        """
        Makes queries to "emprestimos" collection.
        \n
        If field_path, op_string and value equals to "" then returns all the documents
        on collection.
        """
        result = []
        #if all the str args are not ""
        if all([field_path, op_string, value]):
            async for lending in Connector.LENDINGS.where(filter=Connector.field_filter(field_path, op_string, value)).stream():
                result.append(lending.id if only_ids else lending.to_dict())
        else:
            async for lending in Connector.LENDINGS.stream():
                result.append(lending.id if only_ids else lending.to_dict())
        return None if result == [] else result    
    
    async def new(RG: str, lending_id: str) -> LendingReference:
        """
        This function creates a new document on the 'emprestimos' collection and returns a 
        LendingReference object pointing to.
        """
        if Lending.quantity == None: 
            Lending.quantity = len(await Lending.query(only_ids=True))
            
        id = Lending.quantity + 1
        lend_data = {
            'id': str(id),
            'leitor': RG,
            'livro': lending_id,
            'multa': 0,
            'data_emprestimo': Connector.today(),
            'renovado': False,
            'data_finalizacao': False
        }
        await Connector.LENDINGS.document(str(id)).set(lend_data)
        Lending.quantity += 1
        return LendingReference(**lend_data)

        