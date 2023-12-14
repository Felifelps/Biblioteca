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
        DATA[collection] = {
            doc.id: doc.to_dict() for doc in DB.collection(collection).stream()
        }
    await DATA.commit_and_close()
    print('[DATA GOT]')

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
            data_backup = DATA.data
            await DATA.commit_and_close()
        print('[UPLOADING DATA TO FIRESTORE]')
        for collection in data_backup:
            if collection == 'tokens':
                continue
            for id, document in data_backup[collection].items():
                collection_ref = DB.collection(collection)
                collection_ref.document(id).set(document)
        print(
            '[DATA UPLOADED TO FIRESTORE IN',
            str(time.time() - start)[:4],
            'SECONDS]'
        )

        # Waits 1 hour an half
        # And requests every 15 minutes
        for i in range(6):
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
