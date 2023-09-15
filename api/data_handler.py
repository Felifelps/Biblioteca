import firebase_admin, datetime, os
from firebase_admin import firestore_async, credentials, storage
from bcrypt import gensalt, hashpw, checkpw
from threading import Thread

firebase_admin.initialize_app(
    credentials.Certificate(os.path.join('.credentials', 'credentials.json')),
    {"storageBucket": "biblioteca-inteligente-72a6c.appspot.com"}
)

class DataHandler:
    DB = firestore_async.client()
    USERS = DB.collection('users')
    bucket = storage.bucket()
    
    async def new_user(self, username, password):
        if await self.get_user(username) != False: return False
        salt = gensalt()
        user_data = {
            'username': username,
            'salt': salt,
            'password': self.hash_password(password, salt),
            'files': 0
        }
        user = await self.USERS.document(username)
        await user.set(user_data)
        await user.collection('files')
        return self.get_user(username)
    
    async def get_users(self, only_ids=True):
        return [user.id if only_ids else user.to_dict() async for user in self.USERS.stream()]
    
    async def get_user(self, username, password_and_salt=False):
        for user in await self.get_users(False):
            if user['username'] == username: 
                if not password_and_salt:
                    user.pop('password')
                    user.pop('salt')
                return user
        return False
    
    async def get_user_files(self, username, only_ids=True):
        files = []
        async for file in self.USERS.document(username).collection('files').stream():
            files.append(file.id if only_ids else file.to_dict())
        return files
    
    def hash_password(self, password, salt):
        return hashpw(bytes(str(password), encoding='utf-8'), salt)
    
    async def check_password(self, username, password):
        hashed_password = bytes(await self.get_user(username, password_and_salt=True)['password'])
        return checkpw(bytes(str(password), encoding='utf-8'), hashed_password)
    
    async def new_file(self, username, file_obj):
        '''
        quando o usuáro mandar um arquivo, ele fica armazenado temporariamente na pasta temporary
        o servidor manda esse arquivo para o google drive, salva o registro dele no banco de dados e
        apaga o temporário depois
        '''
        id = await self.get_user(username)['files'] + 1
        file_data = {
            'id': id,
            'filename': file_obj.filename,
            'upload_date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        self.upload_file(file_obj)
        await self.DB.document(f'users/{username}/files/{id}').set(file_data)
        await self.USERS.document(username).update({'files': id})
    
    def upload_file(self, file_obj):
        try:
            blob = self.bucket.blob(file_obj.filename)
        except:
            blob = self.bucket.blob(file_obj.name)
        
        Thread(target=lambda: blob.upload_from_file(file_obj)).start()
    
    def remove_all_temp_file(self):
        for file in os.listdir('temporary'):
            os.remove(os.path.join('temporary', file))
    
    async def get_file(self, username, id):
        for file in await self.get_user_files(username, only_ids=False):
            print(str(file['id']) == str(id), id)
            if str(file['id']) == str(id): return file
        return False

    async def get_file_by_name(self, username, filename):
        for file in await self.get_user_files(username, only_ids=False):
            if file['filename'] == filename: return file
        return False
    
    async def delete_file(self, username, id):
        self.bucket.blob()
        self.DB.document(f'users/{username}/files/{id}').delete()

    def delete_user(self, username):
        self.USERS.document(username).delete()
        for file in self.DRIVE.get_files():
            print(file['name'], type(file['name']))
            if username in file['name']:
                self.DRIVE.delete_file(file['name'])
        print(self.DRIVE.get_files())
    
    def download_file(self, username, id):
        file = self.get_file(username, id)
        if file == False: return file
        file_drive_name = f"{username}-{id}-{file['filename']}"
        try:
            self.DRIVE.download_file(file_drive_name, 'temporary', file_download_name=file['filename'])
            return file['filename']
        except:
            return False
