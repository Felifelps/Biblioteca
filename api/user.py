from api.connector import Connector
import datetime

class User(Connector):
    def user_exists(exists=True):
        def decorator(func):
            async def wrapper(*args, **kwargs):
                self, RG, *_ = args
                if RG in await self.all() != exists: 
                    return self.error(f'Usuário {"não encontrado." if exists else "já existente."}')
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    async def all(self, only_ids=True):
        return [i.id if only_ids else i.to_dict() async for i in self.USERS.stream()]
    
    async def get(self, RG):
        try:
            async for user in self.USERS.where(filter=self.field_filter('RG', '==', RG)).stream():
                return user.to_dict()
            return self.error('Usuário não encontrado.')
        except Exception as e:
            return self.error('Um erro ocorreu.', str(e))
    
    @user_exists(False)
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
        try:
            await self.USERS.document(RG).set(user_data)
            return user_data
        except Exception as e:
            return self.error('Um erro ocorreu', str(e))
    
    @user_exists()
    async def update(self, RG, **kwargs):
        try:
            await self.USERS.document(RG).update(kwargs)
        except Exception as e:
            return self.error('Não foi possível atualizar.', str(e))
    
    @user_exists()
    async def delete(self, RG):
        try:
            await self.USERS.document(RG).delete()
        except Exception as e:
            return self.error('Não foi possível excluir.', str(e))
    
    @user_exists()
    async def validate(self, RG):
        try:
            await self.USERS.document(RG).update({'valido': True})
        except Exception as e:
            return self.error('Não foi possível validar.', str(e))
        