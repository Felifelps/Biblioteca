from asyncio import sleep
import json

class Data:
    DATABASE = 'data.json'
    def __init__(self):
        self.__data = None
        self.__open = False
        
    async def connect(self):
        while self.__open:
            await sleep(0.001)
        self.__open = True
        with open(self.DATABASE, 'r') as file:
            self.__data = json.load(file)
    
    async def commit_and_close(self):
        with open(self.DATABASE, 'w') as file:
            file.write(json.dumps(self.__data, indent=4))
        self.__open = False
    
    def __getitem__(self, key):
        return self.__data.get(key, None)
    
    @property
    def data(self):
        return self.__data
        
    def __setitem__(self, key, value):
        self.__data[key] = value

DATA = Data()
