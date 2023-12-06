"""
# apibiblioteca.files

This module contains a class that is responsible to download and upload files to the mega
api. 
"""

from .utils import MEGA
from asyncio import sleep, to_thread
from os import listdir, mkdir, remove, walk
from os.path import exists, getsize, join 

if not exists('temp'):
    mkdir('temp')
    
class Files:
    """
    # apibiblioteca.files.Files
    
    This class contains methods used for manipulate files by the mega api asynchronously
    """
    files = {file['a']['n'] : (key, file) for key, file in MEGA.get_files().items()}

    async def get_file(name: str) -> tuple:
        """
        Gets a file from its name. 
        """
        if name not in Files.files.keys():
            Files.files[name] = await to_thread(lambda: MEGA.find(name))
        return Files.files[name]  
        
    async def get_files() -> dict:
        """
        Gets all the files stored on Mega and saves it in the Files.files attribute,
        then returns it
        """
        Files.files = {file['a']['n'] : (key, file) for key, file in (await to_thread(MEGA.get_files)).items()}
        return Files.files
    
    async def get_link(file):
        return await to_thread(lambda: MEGA.get_link(file))

    async def download(filename: str, rename_to: str=None) -> tuple:
        """
        Downloads a file from Mega by its name to the temp directory.
        
        :param rename_to: An alternative name for the downloaded file.
        """
        file = await Files.get_file(filename)
        total_size = 0
        for dirpath, _, filenames in walk('temp'):
            for filename in filenames:
                total_size += getsize(join('temp', filename))
                print(filename, ':', (getsize(join('temp', filename))/1024)/1024, 'MB')
        mega_bytes_size = (total_size/1024)/1024
        if mega_bytes_size > 50:
            for file in listdir('temp'):
                await Files.future_remove(join('temp', file), 5)
        try:
            await to_thread(lambda: MEGA.download(
                file, 
                dest_path='temp', 
                dest_filename=rename_to
            ))
        except PermissionError as e:
            pass
        return file
    
    async def upload(file_path: str, rename_to: str=None, temp: bool=True, delete: bool=True) -> None:
        """
        Uploads a file from some path to Mega, then deletes it.
        
        :param rename_to: An allternative name for the uploaded file
        :param temp: Looks in temporary directory if True, else looks for the file_path
        itself
        """
        file_path = Files.temp(file_path) if temp else file_path
        if not exists(file_path):
            raise FileNotFoundError('File not found')
        try:
            await to_thread(lambda: MEGA.upload(
                file_path, 
                dest_filename=rename_to
            ))
        except PermissionError as e:
            pass
        remove(file_path) if delete else print()
        
    async def destroy_file(file_name):
        await to_thread(
            MEGA.delete_url(
                await Files.get_link(
                    await Files.get_file(file_name)
                    )
                )
            )
        
    async def future_remove(name: str, time=150) -> None:
        """
        Sleeps a time then deletes the given file
        """
        print('Removing', name, 'in', time, 'seconds')
        await sleep(time)
        try:
            remove(name)
        except FileNotFoundError as e:
            pass
        print(name, 'removed')
    
    def temp(name: str) -> str:
        """
        Returns 'temp' joined with name
        """
        return join('temp', name)
    
    
        
