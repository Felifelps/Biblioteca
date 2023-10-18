from .utils import DB
from .data import DATA
import datetime
from threading import Thread
import time

def _watcher():
    print('[WATCHER STARTED]')
    while True:
        # Check every three hours
        time.sleep(10800)
        if datetime.datetime.now().hour in [22, 23, 0, 1]:
            DB.set(DATA.data)
            print('[DATA UPLOADED TO FIRESTORE]')
            
WATCHER = Thread(target=_watcher, daemon=True)