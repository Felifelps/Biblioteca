from .connector import DB
from .data import Data
import datetime
from threading import Thread
import time

def _watcher():
    while True:
        time.sleep(5)
        if datetime.datetime.now().hour == 0:
            DB.set(Data.data)
            print('Updated')
        
watcher = Thread(target=_watcher, daemon=True)