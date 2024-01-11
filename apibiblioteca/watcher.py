from asyncio import new_event_loop
from .utils import DB
from .models import Token, Book, model_to_dict, db
import requests
from threading import Thread
import time, datetime


async def _watcher():
    print('[WATCHER STARTED]')
    
    while True:
        print('[AUTOREQUESTING]')
        response = requests.post(
            'https://bibliotecamilagres-503s.onrender.com/books'
        )
        print('[REQUEST DONE]', response.status_code)
        time.sleep(900)
        
        if datetime.datetime.now().hour == 11:
            
            db.commit()
            
            db.close()
            
            db.connect()
        
            start = time.time()

            print('[UPDATING TOKENS]')
            
            for token in Token.select():
                token.validate()
                
            print('[TOKENS UPDATED]')
                
            print('[UPLOADING DATA TO FIRESTORE]')
            
            books_collection = DB.collection('books')
            
            for book in Book.select():
                try:
                    books_collection.document(str(book.id)).set(model_to_dict(book))
                except Exception as e:
                    print(e)
                    break
                
            print(
                '[DATA UPLOADED TO FIRESTORE IN',
                str(time.time() - start)[:4],
                'SECONDS]'
            )

def watcher():
    loop = new_event_loop()
    loop.run_until_complete(_watcher())


WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)
