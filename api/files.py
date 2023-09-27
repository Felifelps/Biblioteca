"""
# api.files

This module contains a class that is responsible to download and upload files to the mega
api. 
"""

from api.connector import Connector, MEGA
from asyncio import to_thread
from os import path, remove

class Files:
    """
    # api.files.Files
    
    This class contains methods used for manipulate files by the mega api asynchronously
    """
    files = {file['a']['n'] : (key, file) for key, file in MEGA.get_files().items()}

    @Connector.catch_error
    async def get_file(name: str) -> tuple:
        """
        Gets a file from its name. 
        """
        if name not in Files.files.keys():
            Files.files[name] = await to_thread(lambda: MEGA.find(name))
        return Files.files[name]  
        
    @Connector.catch_error
    async def get_files() -> dict:
        """
        Gets all the files stored on Mega and saves it in the Files.files attribute,
        then returns it
        """
        Files.files = {file['a']['n'] : (key, file) for key, file in (await to_thread(MEGA.get_files)).items()}
        return Files.files

    @Connector.catch_error
    async def download(filename: str, rename_to: str=None) -> tuple:
        """
        Downloads a file from Mega by its name to the temp directory.
        
        :param rename_to: An alternative name for the downloaded file.
        """
        
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
    
    @Connector.catch_error
    async def upload(file_path: str, rename_to: str=None, temp: bool=True) -> None:
        """
        Uploads a file from some path to Mega, then deletes it.
        
        :param rename_to: An allternative name for the uploaded file
        :param temp: Looks in temporary directory if True, else looks for the file_path
        itself
        """
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
    
    def temp(name: str) -> str:
        """
        Returns 'temp' joined with name
        """
        return path.join('temp', name)
    
    def remove(name: str, temp: bool=True) -> None:
        """
        Deletes the given file
        
        :param temp: Looks in temporary directory if True, else looks for the file_path
        itself
        """
        remove(Files.temp(name) if temp else name)
