from asyncio import new_event_loop
from .utils import DB, today
from .data import DATA
from .email import Email
import datetime
import requests
from threading import Thread
import time

async def _watcher():
    print('[WATCHER STARTED]')
    while True:
        time.sleep(30) #43200
        # Check every three hours
        if True or datetime.datetime.now().hour in [22, 23, 0, 1]:
            
            start = time.time()
            await DATA.connect()
            """
            
            print('[UPLOADING DATA TO FIRESTORE]')
            for collection in DATA.data:
                for id, document in DATA[collection].items(): 
                    collection_ref = DB.collection(collection)
                    collection_ref.document(id).set(document)
            print(f'[DATA UPLOADED TO FIRESTORE IN {time.time() - start:.2f} SECONDS]')
            """
            print('[UPDATING LENDINGS AND SENDING EMAILS]')
            for lending_id, lending in DATA['lendings'].items():
                print(lending_id)
                if not lending['data_finalizacao']:
                    user = DATA['users'][lending['leitor']]
                    lending_limit = 20 if lending['renovado'] else 10
                    lending_time = (datetime.datetime.today() - datetime.datetime.strptime(lending['data_emprestimo'], '%d/%m/%y às %H:%M:%S')).days
                    if not lending['pego'] and lending_time > 2:
                        lending.update({'data_finalizacao': today()})
                        user.update({'livro': False})
                        DATA['books'][lending['livro']].update({'leitor': False})
                    elif lending_time > lending_limit:
                        lending.update({'multa': 0.10 * (lending_time - lending_limit)})
                    DATA['lendings'].update({lending_id: lending}) 
                    
            await DATA.commit_and_close()
            print('[LENDINGS UPDATED]')
        
def watcher():    
    loop = new_event_loop()
    loop.run_until_complete(_watcher())
        
WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)