from asyncio import new_event_loop
from .utils import DB, get_today_minus_date_days
from .data import DATA
import requests
from threading import Thread
import time


async def _watcher():
    print('[WATCHER STARTED]')

    '''
    print('[GETTING DATA FROM FIRESTORE]')
    await DATA.connect()
    for collection in DATA.data.keys():
        DATA[collection] = {
            doc.id: doc.to_dict() for doc in DB.collection(collection).stream()
        }
    await DATA.commit_and_close()
    print('[DATA GOT]')
    '''
    
    books_uploaded = 0
    requests_diary_limit = 19500

    while True:
        start = time.time()
        await DATA.connect()
        try:
            print('[UPDATING TOKENS]')
            for token, date in DATA['tokens'].items():
                if get_today_minus_date_days(date) > 0:
                    DATA['tokens'].pop(token)
            print('[TOKENS UPDATED]')
        finally:
            data_backup_keys = list(DATA['books'].keys())
            data_backup_values = list(DATA['books'].values())
            await DATA.commit_and_close()
            
        print('[UPLOADING DATA TO FIRESTORE]')
        
        if len(data_backup_keys) > requests_diary_limit:
            final_books = books_uploaded + requests_diary_limit 
        else:
            final_books = len(data_backup_keys) - 1
        
        for document in data_backup_values[books_uploaded: final_books]:
            collection_ref = DB.collection('books')
            collection_ref.document(data_backup_keys[books_uploaded]).set(document)
            books_uploaded += 1
            
        if books_uploaded >= len(data_backup_keys):
            books_uploaded = 0
            
        print(
            '[DATA UPLOADED TO FIRESTORE IN',
            str(time.time() - start)[:4],
            'SECONDS]'
        )

        # Waits 1 day
        # And requests every 15 minutes
        for i in range(96):
            print('[AUTOREQUESTING]')
            response = requests.post(
                'https://bibliotecamilagres-503s.onrender.com/books'
            )
            print('[REQUEST DONE]', response.status_code)
            time.sleep(900)


def watcher():
    loop = new_event_loop()
    loop.run_until_complete(_watcher())


WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)
