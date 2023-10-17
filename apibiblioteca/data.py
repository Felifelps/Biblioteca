from filelock import FileLock
import json

class Data:
    DATABASE = 'data.json'
    __data = None
    def __lock_database(self):
        return FileLock(self.DATABASE + '.lock')

    def __read(self):
        with self.__lock_database():
            with open(self.DATABASE, 'r') as data:
                self.data = json.load(data)
            
    def update(self, updated_data):
        with self.__lock_database():
            with open(self.DATABASE, 'w') as data:
                data.write(json.dumps(updated_data))
            self.__data = updated_data
            
    @property
    def data(self):
        if not self.__data:
            self.__data = self.__read()
        return self.__data
    
    @data.setter
    def data(self):
        raise 'Data is an only-read property'

