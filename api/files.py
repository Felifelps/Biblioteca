from api.connector import Connector
from asyncio import sleep
from os import remove, path
from queue import Queue
from threading import current_thread, Thread
from time import time

mega = Connector.MEGA

class Files:
    files = {file['a']['n'] : (key, file) for key, file in mega.get_files().items()}
    mega = mega

    def __get_file_thread(name):
        global file_got
        Files.files[name] = mega.find(name)
        file_got = True

    async def get_file(name, max_attempts=50):
        if name not in Files.files.keys():
            global file_got
            file_got = False
            Thread(target=lambda: Files.__get_file_thread(name)).start()
            for i in range(max_attempts + 2):
                if file_got:
                    break
                await sleep(2)
            if i > max_attempts: raise Exception('Maximum attempts reached')
        return Files.files[name]  
    
    def __get_files_thread():
        global files_got
        Files.files = {file['a']['n'] : (key, file) for key, file in mega.get_files().items()}
        files_got = True
        
    async def get_files(max_attempts=50):
        global Files, files_got
        files_got = False
        Thread(target=Files.__get_files_thread).start()
        for i in range(max_attempts + 2):
            if files_got:
                return Files.files 
            await sleep(1)
        raise Exception('Maximum attempts reached')

    def __download_thread(file, rename_to):
        global file_downloaded
        try: 
            mega.download_url(
                mega.get_link(file), 
                dest_path='temp', 
                dest_filename=rename_to
            )
        except Exception as e:
            print(e)
        file_downloaded = True   

    async def download(filename, rename_to=None, max_attempts=50):
        file = await Files.get_file(filename)
        global file_downloaded 
        file_downloaded = False 
        Thread(target=lambda: Files.__download_thread(file, rename_to)).start()
        for i in range(max_attempts + 2):
            if file_downloaded:
                return file 
            await sleep(2)
        raise Exception('Maximum attempts reached')
        
            
    def __await__(self):
        yield from self.download()
    
    def upload(file_path, rename_to=None, temp=True):
        if not path.exists(Files.temp(file_path)):
            raise FileNotFoundError()
        try:
            mega.upload(
                Files.temp(file_path) if temp else file_path, 
                dest_filename=rename_to
            )
        except Exception as e:
            print(e)
        Files.remove(file_path)
    
    def temp(name):
        return path.join('temp', name)
    
    def remove(name):
        remove(Files.temp(name))
