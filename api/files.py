from api.connector import MEGA
from asyncio import to_thread
from os import path, remove

class Files:
    files = {file['a']['n'] : (key, file) for key, file in MEGA.get_files().items()}

    async def get_file(name):
        if name not in Files.files.keys():
            Files.files[name] = await to_thread(lambda: MEGA.find(name))
        return Files.files[name]  
        
    async def get_files():
        Files.files = {file['a']['n'] : (key, file) for key, file in (await to_thread(MEGA.get_files)).items()}
        return Files.files

    async def download(filename, rename_to=None):
        file = await Files.get_file(filename)
        try:
            await to_thread(lambda: MEGA.download(
                file, 
                dest_path='temp', 
                dest_filename=rename_to
            ))
        except PermissionError as e:
            pass
        return file
    
    async def upload(file_path, rename_to=None, temp=True):
        file_path = Files.temp(file_path) if temp else file_path
        if not path.exists(file_path):
            raise FileNotFoundError('File not found')
        try:
            await to_thread(lambda: MEGA.upload(
                file_path, 
                dest_filename=rename_to
            ))
        except PermissionError as e:
            pass
        Files.remove(file_path, temp=temp)
    
    def temp(name):
        return path.join('temp', name)
    
    def remove(name, temp=True):
        remove(Files.temp(name) if temp else name)
