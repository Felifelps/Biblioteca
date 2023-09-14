import firebase_admin, datetime, os
from firebase_admin import firestore_async, credentials, storage
from bcrypt import gensalt, hashpw, checkpw

firebase_admin.initialize_app(
    credentials.Certificate(os.path.join('credentials', 'credentials.json'))
)

class DataHandler:
    DB = firestore_async.client()
    USERS = DB.collection('users')
    
    def new_user(self, username, password):
        if self.get_user(username) != False: return False
        salt = gensalt()
        user_data = {
            'username': username,
            'salt': salt,
            'password': self.hash_password(password, salt),
            'files': 0
        }
        self.USERS.document(username).set(user_data)
        self.USERS.document(username).collection('files')
        return self.get_user(username)
    
    def get_users(self, only_ids=True):
        return [user.id if only_ids else user.to_dict() for user in self.USERS.stream()]
    
    def get_user(self, username, password_and_salt=False):
        for user in self.get_users(False):
            if user['username'] == username: 
                if not password_and_salt:
                    user.pop('password')
                    user.pop('salt')
                return user
        return False
    
    def get_user_files(self, username, only_ids=True):
        files = []
        for file in self.USERS.document(username).collection('files').stream():
            print(file)
            files.append(file.id if only_ids else file.to_dict())
        return files
    
    def hash_password(self, password, salt):
        return hashpw(bytes(str(password), encoding='utf-8'), salt)
    
    def check_password(self, username, password):
        hashed_password = bytes(self.get_user(username, password_and_salt=True)['password'])
        return checkpw(bytes(str(password), encoding='utf-8'), hashed_password)
    
    def new_file(self, username, filename):
        '''
        quando o usuáro mandar um arquivo, ele fica armazenado temporariamente na pasta temporary
        o servidor manda esse arquivo para o google drive, salva o registro dele no banco de dados e
        apaga o temporário depois
        '''
        id = self.get_user(username)['files'] + 1
        file_data = {
            'id': id,
            'filename': filename,
            'upload_date': datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        temporary_path = os.path.join('temporary', filename)
        self.DRIVE.upload_file(temporary_path, file_name=f'{username}-{id}-{filename}')
        self.remove_all_temp_file()
        self.DB.document(f'users/{username}/files/{id}').set(file_data)
        self.USERS.document(username).update({'files': id})
    
    def remove_all_temp_file(self):
        for file in os.listdir('temporary'):
            os.remove(os.path.join('temporary', file))
    
    def get_file(self, username, id):
        for file in self.get_user_files(username, only_ids=False):
            print(str(file['id']) == str(id), id)
            if str(file['id']) == str(id): return file
        return False

    def get_file_by_name(self, username, filename):
        for file in self.get_user_files(username, only_ids=False):
            if file['filename'] == filename: return file
        return False
    
    def delete_file(self, username, id):
        self.DRIVE.delete_file(f'{username}-{id}-{self.get_file(username, id)["filename"]}')
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



