from .utils import DB
from .data import DATA
import datetime
import requests
from threading import Thread
import time

def _watcher():
    print('[WATCHER STARTED]')
    while True:
        time.sleep(10800)
        # Check every three hours
        if datetime.datetime.now().hour in [22, 23, 0, 1]:
            start = time.time()
            print('[UPLOADING DATA TO FIRESTORE]')
            for collection in DATA.data:
                for id, document in DATA.data[collection].items(): 
                    collection_ref = DB.collection(collection)
                    collection_ref.document(id).set(document)
            print(f'[DATA UPLOADED TO FIRESTORE IN {time.time() - start:.2f} SECONDS]')
        
WATCHER = Thread(target=_watcher, daemon=True)