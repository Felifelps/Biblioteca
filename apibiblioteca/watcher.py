from asyncio import new_event_loop
from .utils import DB, get_today_minus_date_days
from .data import DATA
import requests
from threading import Thread
import time

async def _watcher():
    print('[WATCHER STARTED]')

    print('[GETTING DATA FROM FIRESTORE]')
    await DATA.connect()    
    for collection in DATA.data.keys():
        DATA[collection] = {doc.id: doc.to_dict() for doc in DB.collection(collection).stream()}
    await DATA.commit_and_close()
    print('[DATA GOT]')

    while True:
        print('[AUTO-REQUESTING]')
        
        try:
            response = requests.get('https://apibiblioteca.2.ie-1.fl0.io/register_key')
            if response.status_code == 200:
                print(response.text)
            else:
                print('[REQUEST FAILED]')
        except:
            pass
        
        start = time.time()
        await DATA.connect()
        try:
            try:
                print('[UPDATING TOKENS]')
                for token, date in DATA['tokens'].items():
                    if get_today_minus_date_days(date) > 0:
                        DATA['tokens'].pop(token)
                print('[TOKENS UPDATED]')
            except: 
                pass
            
            print('[UPLOADING DATA TO FIRESTORE]')
            for collection in DATA.data:
                if collection == 'tokens': continue
                for id, document in DATA[collection].items(): 
                    collection_ref = DB.collection(collection)
                    collection_ref.document(id).set(document)
            print(f'[DATA UPLOADED TO FIRESTORE IN {time.time() - start:.2f} SECONDS]')
        except Exception as e:
            print(e)
        finally:
            await DATA.commit_and_close()
    
        # Waits 1 hour an half
        time.sleep(5400)

def watcher():    
    loop = new_event_loop()
    loop.run_until_complete(_watcher())
        
WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)