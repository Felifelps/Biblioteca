from .utils import DB
from .data import DATA
import datetime
import requests
from threading import Thread
import time

def _auto_requesting():
    print('[AUTO REQUESTING STARTED]')
    while True:
        # Requests every 25 minutes
        time.sleep(1500)
        print('[REQUESTING TO SERVER]')
        try:
            response = requests.get('http://127.0.0.1:8080/register_key')
            if response.status_code == 200:
                print('[REQUEST DONE]')
        except Exception as e:
            print(e)

def _uploader():
    print('[UPLOADER STARTED]')
    while True:
        # Check every three hours
        time.sleep(10800)
        if datetime.datetime.now().hour in [22, 23, 0, 1]:
            start = time.time()
            print('[UPLOADING DATA TO FIRESTORE]')
            for collection in DATA.data:
                for id, document in DATA.data[collection].items(): 
                    collection_ref = DB.collection(collection)
                    collection_ref.document(id).set(document)
            print(f'[DATA UPLOADED TO FIRESTORE IN {time.time() - start:.2f} SECONDS]')
        
AUTO_REQUESTING = Thread(target=_auto_requesting, daemon=True)
UPLOADER = Thread(target=_uploader, daemon=True)