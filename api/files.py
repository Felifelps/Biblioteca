from api.connector import Connector
from os import remove, path
from queue import Queue
from threading import Lock, Thread

queue = Queue()

class Files:
    
    def update_files_reference(func):
        def wrapper(*args, **kwargs):
            value = func()
            Thread(target=lambda: queue.put(Connector.MEGA.get_files())).start()
            return value
        return wrapper
    
    def files():
        return queue.get() if queue.queue.clear() == None else None
    
    @update_files_reference
    def upload_file(file_path, filename=None):
        if not filename: filename = path.basename(file_path)
        Thread(target=lambda: Connector.MEGA.upload(Files.temp(file_path))).start()
    
    def temp(name):
        return path.join('temp', name)
    
    def remove(name):
        remove(Files.temp(name))
