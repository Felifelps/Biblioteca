from filelock import FileLock
import json

class Data:
    DATABASE = 'data.json'
    FILELOCK = FileLock(DATABASE + '.lock')
    def __init__(self):
        self.__data = None
        
    def save_after_updates(self, func):
        def wrapper(*args, **kwargs):
            self.connect()
            result = func(*args, **kwargs)
            self.commit_and_close()
            return result
        return wrapper
        
    def connect(self):
        try:
            self.FILELOCK.acquire()
            with open(self.DATABASE, 'r') as file:
                self.__data = json.load(file)
        except:
            pass
    
    def commit_and_close(self):
        with open(self.DATABASE, 'w') as file:
            file.write(json.dumps(self.__data, indent=4))
        self.FILELOCK.release()
        
    def __getter__(self):
        return self.__data
    
    def __getitem__(self, key):
        return self.__data.get(key, None)
    
    def __setitem__(self, key, value):
        self.__data[key] = value

DATA = Data()