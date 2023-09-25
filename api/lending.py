from api.connector import Connector
    
class LendingReference:
    def __init__(self, **kwargs):
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def __str__(self) -> str:
        return f'<LendingReference(id={self.id}, livro="{self.livro}", leitor="{self.leitor}")>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.fields}
    
    @Connector.catch_error   
    async def save(self):
        await Connector.LENDINGS.document(self.id).update(self.to_dict())
    
    @Connector.catch_error
    async def delete(self):
        await Connector.LENDINGS.document(self.id).delete()
        del self

class Lending:
    quantity = None
    @Connector.catch_error
    async def query(field_path="", op_string="", value="", only_ids=False):
        result = []
        #if all the str args are not ""
        if all([field_path, op_string, value]):
            async for lending in Connector.LENDINGS.where(filter=Connector.field_filter(field_path, op_string, value)).stream():
                result.append(lending.id if only_ids else lending.to_dict())
        else:
            async for lending in Connector.LENDINGS.stream():
                result.append(lending.id if only_ids else lending.to_dict())
        return None if result == [] else result    
    
    async def new(RG, book_id):
        if Lending.quantity == None: 
            Lending.quantity = len(await Lending.query(only_ids=True))
            
        id = Lending.quantity + 1
        lend_data = {
            'id': str(id),
            'leitor': RG,
            'livro': book_id,
            'multa': 0,
            'data_emprestimo': Connector.today(),
            'renovado': False,
            'data_finalizacao': False
        }
        await Connector.LENDINGS.document(str(id)).set(lend_data)
        Lending.quantity += 1
        return LendingReference(**lend_data)

        