from api.connector import Connector
import datetime, asyncio

class User(Connector):
    def user_exists(RG):
        def inner(self, func):
            if 'error' in asyncio.ensure_future(self.get(RG)): 
                return self.error('Usuário não encontrado.')
            return asyncio.ensure_future(func()) 
        return inner
    
    async def new(
        self, 
        RG,
        nome,
        data_nascimento,
        local_nascimento,
        CEP,
        tel_pessoal,
        residencia,
        profissao="",
        tel_profissional="",
        escola="",
        curso_serie=""
    ):
        if 'error' not in await self.get(RG): return self.error('RG já cadastrado.')
        user_data = {
            'RG': RG,
            'nome': nome,
            'data_nascimento': data_nascimento,
            'local_nascimento': local_nascimento,
            'CEP': CEP,
            'tel_pessoal': tel_pessoal,
            'residencia': residencia,
            'profissao': profissao,
            'tel_profissional': tel_profissional,
            'escola': escola,
            'curso_serie': curso_serie,
            'data_cadastro': datetime.datetime.today().strftime('%d/%m/%y'),
            'valido': False        
        }
        await self.USERS.document(RG).set(user_data)
        return user_data
    
    async def update(self, RG, *kwargs):
        await self.USERS.document(RG).update(kwargs)
    
    @user_exists
    async def delete(self, RG):
        try:
            await self.USERS.document(RG).delete()
        except:
            return self.error('Não foi possível excluir')
        
    async def all(self, only_ids=True):
        return [i.id if only_ids else i.to_dict() async for i in self.USERS.list_documents()]
    
    async def get(self, RG):
        async for user in self.USERS.where(filter=self.field_filter('RG', '==', RG)).stream():
            return user.to_dict()
        return self.error('Usuário não encontrado')
    
    async def validate(self, RG):
        await self.USERS.document(RG).update({
            'valido': True
        })
        