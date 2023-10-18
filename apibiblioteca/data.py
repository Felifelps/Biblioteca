from filelock import FileLock
import json

class Data:
    DATABASE = 'data.json'
    __data = {}
    def __init__(self):
        self.__data = self.__read()
    
    def __lock_database(self):
        return FileLock(self.DATABASE + '.lock')

    def __read(self):
        with self.__lock_database():
            with open(self.DATABASE, 'r') as data:
                return json.load(data)
            
    def update(self, field, updated_data):
        with self.__lock_database():
            with open(self.DATABASE, 'w') as data:
                self.__data[field].update(updated_data)
                data.write(json.dumps(self.__data, indent=4))
                
    def change(self, new_data):
        with self.__lock_database():
            with open(self.DATABASE, 'w') as data:
                data.write(json.dumps(new_data, indent=4))
            
    @property
    def data(self):
        self.__data = self.__read()
        return self.__data

DATA = Data()