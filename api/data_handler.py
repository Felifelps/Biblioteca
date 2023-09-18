import firebase_admin, datetime, os
from firebase_admin import firestore_async, credentials, storage
from threading import Thread

firebase_admin.initialize_app(
    credentials.Certificate(os.path.join('.credentials', 'credentials.json')),
    {"storageBucket": "biblioteca-inteligente-72a6c.appspot.com"}
)       

class DataHandler:
    DB = firestore_async.client()
    USERS = DB.collection('users')
    bucket = storage.bucket()
    
    async def new_user(
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
        if await self.get_user(nome) != False: return False
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
    
    async def update_user(self, RG, *kwargs):
        await self.USERS.document(RG).update(kwargs)
        
    async def delete_user(self, RG):
        await self.USERS.document(RG).delete()
    
    async def get_users(self, only_ids=True):
        return [user.id if only_ids else user.to_dict() async for user in self.USERS.stream()]
    
    async def get_user(self, RG):
        for user in await self.get_users(False):
            if user['RG'] == RG: return user
        return False
    
    async def validate_user(self, RG):
        await self.USERS.document(RG).update({
            'valido': True
        })
        
    def get_file_by_name(self, name):
        return [blob for blob in self.bucket.list_blobs(prefix='') if name in blob.name]
        
    def upload_user_images(self, RG, request_file) -> None:
        self.upload_file(request_file, f'{RG}-')
    
    def upload_file(self, request_file, name=''):
        if name == '': name = request_file.filename
        with open(os.path.join('temp', name), 'wb') as base_file:
            for i in request_file: base_file.write(i)
        blob = self.bucket.blob(name)
        Thread(target=lambda: blob.upload_from_filename('teste.file')).start()
        os.remove(os.path.join('temp', name))

    
    def download_file(self, username, id):
        pass
