from api.connector import Connector
from threading import Thread

import os

class Files(Connector):
    def upload_file(self, file_path, filename=None):
        if not filename: filename = os.path.basename(file_path)
        Thread(target=lambda: self.MEGA.upload(self.temp(file_path))).start()
        
    def temp(self, name):
        return os.path.join('temp', name)
    
    def remove(self, name):
        os.remove(self.temp(name))
