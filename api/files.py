from api.connector import Connector
from threading import Thread

import os

class Files(Connector):
    def get_file_by_name(self, name):
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
        Thread(target=self.__upload_file(request_file, name)).start()
        
    def __upload_file(self, request_file, name):
        with open(self.temp(name), 'wb') as base_file:
            for i in request_file: base_file.write(i)
        blob = self.bucket.blob(name)
        blob.upload_from_filename(self.temp(name))
        self.remove(name)
    
    def remove(self, name):
        os.remove(self.temp(name))
