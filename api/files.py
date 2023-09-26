from api.connector import Connector
from os import remove, path
from queue import Queue
from threading import current_thread, Thread
from time import time

mega = Connector.MEGA

class Files:
    files = {file['a']['n'] : (key, file) for key, file in mega.get_files().items()}
    
    def get_file(name):
        if name not in Files.files.keys():
            Files.files[name] = mega.find(name)
        print(Files.files)
        return Files.files[name]  
    
    def get_files():
        Files.files = {file['a']['n'] : (key, file) for key, file in mega.get_files().items()}
        return Files.files 
    
    def download(filename, rename_to=None, temp=True):
        file = Files.get_file(filename)
        Thread(target=lambda: mega.download_url(mega.get_link(file), dest_filename=rename_to)).start()
    
    def upload(file_path, filename=None, temp=True):
        if not filename: filename = path.basename(file_path)
        Thread(target=lambda: mega.upload(Files.temp(file_path) if temp else file_path)).start()
    
    def temp(name):
        return path.join('temp', name)
    
    def remove(name):
        remove(Files.temp(name))
