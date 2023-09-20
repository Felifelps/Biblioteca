from api.connector import Connector
import datetime

class User:
    def user_exists(func):
        async def wrapper(*args, **kwargs):
            RG, *_ = args
            if RG not in await User.all(): 
                return Connector.message(f'Usuário não encontrado.')
            return await func(*args, **kwargs)
        return wrapper
    
    @Connector.catch_error
    async def all(only_ids=True):
        return [user.id if only_ids else user.to_dict() async for user in Connector.USERS.stream()]
    
    @Connector.catch_error
    async def get(RG):
        async for user in Connector.USERS.where(filter=Connector.field_filter('RG', '==', RG)).stream():
            return user.to_dict()
        return Connector.message('Usuário não encontrado.')
    
    @Connector.catch_error
    async def new( 
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
        if RG in await User.all(): 
            return Connector.message('Usuário já existente')
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
            await Connector.USERS.document(RG).set(user_data)
            return user_data
        except Exception as e:
            return Connector.message('Um erro ocorreu', str(e))
    
    @Connector.catch_error
    @user_exists
    async def update(RG, **kwargs):
        await Connector.USERS.document(RG).update(kwargs)
        return Connector.message('Usuário atualizado.')
    
    @Connector.catch_error
    @user_exists
    async def delete(RG):
        await Connector.USERS.document(RG).delete()
        return Connector.message('Usuário excluído.')
    
    @Connector.catch_error
    @user_exists
    async def validate(RG):
        await Connector.USERS.document(RG).update({'valido': True})
        return Connector.message('Usuário validado.')