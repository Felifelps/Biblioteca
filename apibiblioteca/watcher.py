from asyncio import new_event_loop
from .utils import DB, MESSAGES, today
from .data import DATA
from .email import Email
import datetime
from threading import Thread
import time, json

def get_today_minus_date_days(date):
    return (datetime.datetime.today() - datetime.datetime.strptime(date, '%d/%m/%y às %H:%M:%S')).days

async def _watcher():
    print('[WATCHER STARTED]')

    print('[GETTING DATA FROM FIRESTORE]')
    await DATA.connect()
    for collection in DATA.data.keys():
        DATA[collection] = {doc.id: doc.to_dict() for doc in DB.collection(collection).stream()}
    await DATA.commit_and_close()
    print('[DATA GOT]')

    while True:
        print('[WATCHER - CHECKING TIME]')
        if datetime.datetime.now().hour in [4, 5, 6, 7]:
            start = time.time()
            await DATA.connect()
            
            print('[UPDATING LENDINGS AND SENDING EMAILS]')
            for lending_id, lending in DATA['lendings'].items():
                if lending['data_finalizacao']:
                    continue
                user = DATA['users'][lending['leitor']]
                book = DATA['books'][lending['livro']]
                if not lending['pego']:
                    lending_time = get_today_minus_date_days(lending['data_emprestimo'])
                    if lending_time > 2:
                        lending.update({'data_finalizacao': today()})
                        user.update({'livro': False})
                        for copy in DATA['books'][lending['livro']]['copies']:
                            if copy['leitor'] == lending['leitor']:
                                copy.update({'leitor': False})
                        await Email.message(
                            user['email'], 
                            MESSAGES['lending_finalized_not_get'](
                                user['nome'], 
                                book['titulo']
                            ),
                            'Biblioteca - Empréstimo cancelado'
                        )
                else:
                    lending_time = get_today_minus_date_days(lending['pego'])
                    if lending_time > 10:
                        lending.update({'multa': 0.1 * (lending_time - 10)})
                        await Email.message(
                            user['email'], 
                            MESSAGES['multa_number'](
                                user['nome'], 
                                book['titulo'], 
                                0.1 * (lending_time - 10)
                            ),
                            f'Biblioteca - Devolução atrasada'
                        )
                    else:
                        await Email.message(
                            user['email'], 
                            MESSAGES['days_to_renew_or_return'](
                                user['nome'], 
                                book['titulo'], 
                                10 - lending_time
                            ),
                            f"Biblioteca - Faltam {10 - lending_time} dia{'s' if lending_time == 9 else ''}"
                        )
                DATA['lendings'].update({lending_id: lending})
                
            print('[LENDINGS UPDATED]')
            
            print('[UPLOADING DATA TO FIRESTORE]')
            for collection in DATA.data:
                for id, document in DATA[collection].items(): 
                    collection_ref = DB.collection(collection)
                    collection_ref.document(id).set(document)
            print(f'[DATA UPLOADED TO FIRESTORE IN {time.time() - start:.2f} SECONDS]')
            
            await DATA.commit_and_close()
        
        # Check every three hours
        time.sleep(10800) #43200
        
def watcher():    
    loop = new_event_loop()
    loop.run_until_complete(_watcher())
        
WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)