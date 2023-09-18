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
        
    def get_file_by_name(self, name) -> list[storage.storage.Blob]:
        return [blob for blob in self.bucket.list_blobs(prefix='') if name in blob.name]
    
    def temp(self, name):
        return os.path.join('temp', name)
    
    def download_files_by_name(self, name):
        blobs = self.get_file_by_name(name)
        for blob in blobs: Thread(target=blob.download_to_filename(self.temp(blob.name))).start()
        
    def upload_user_images(self, RG, request_file) -> None:
        files = len(self.get_file_by_name(RG)) + 1
        if files > 3: return
        self.upload_file(request_file, name=f'{RG}_{files}{os.path.splitext(request_file.filename)[1]}')
    
    def upload_file(self, request_file, name=None):
        if name == None: name = request_file.filename
        Thread(target=self._upload_file(request_file, name)).start()
        
    def _upload_file(self, request_file, name):
        with open(self.temp(name), 'wb') as base_file:
            for i in request_file: base_file.write(i)
        blob = self.bucket.blob(name)
        blob.upload_from_filename(self.temp(name))
        self.remove(name)
    
    def remove(self, name):
        os.remove(self.temp(name))
