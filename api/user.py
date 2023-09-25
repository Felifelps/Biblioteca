from api.connector import Connector

class UserReference:
    def __init__(self, **kwargs):
        self.fields = list(kwargs.keys())
        for key, value in kwargs.items():
            setattr(self, key, value)
        
    def __str__(self) -> str:
        return f'<UserReference(RG="{self.RG}", nome="{self.nome}")>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self):
        return {attr: getattr(self, attr) for attr in self.fields}
    
    @Connector.catch_error   
    async def save(self):
        await Connector.USERS.document(self.RG).update(self.to_dict())
    
    @Connector.catch_error
    async def delete(self):
        await Connector.USERS.document(self.RG).delete()
        del self

class User:
    @Connector.catch_error
    async def query(field_path="", op_string="", value="", only_ids=False):
        result = []
        #if all the str args are not ""
        if all([field_path, op_string, value]):
            async for user in Connector.USERS.where(filter=Connector.field_filter(field_path, op_string, value)).stream():
                result.append(user.id if only_ids else user.to_dict())
        else:
            async for user in Connector.USERS.stream():
                result.append(user.id if only_ids else user.to_dict())
        return None if result == [] else result     
    
    @Connector.catch_error
    async def new( 
        RG,
        nome,
        data_nascimento,
        local_nascimento,
        email,
        CEP,
        tel_pessoal,
        residencia,
        profissao="",
        tel_profissional="",
        escola="",
        curso_serie="",
        **kwargs
    ):
        if RG in await User.query(only_ids=True): 
            return Connector.message('Usuário já existente')
        user_data = {
            'RG': RG,
            'nome': nome,
            'data_nascimento': data_nascimento,
            'local_nascimento': local_nascimento,
            'email': email,
            'CEP': CEP,
            'tel_pessoal': tel_pessoal,
            'residencia': residencia,
            'profissao': profissao,
            'tel_profissional': tel_profissional,
            'escola': escola,
            'curso_serie': curso_serie,
            'data_cadastro': Connector.today(),
            'valido': False,
            'favoritos': [],
            'livro': False     
        }
        await Connector.USERS.document(RG).set(user_data)
        return UserReference(**user_data)
