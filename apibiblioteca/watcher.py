from asyncio import new_event_loop
from .utils import DB
from .models import Token, Book, db, model_to_dict
from threading import Thread
import time, datetime


async def _watcher():
    print('[WATCHER STARTED]')
    
    print('[GETTING BOOKS FROM FIRESTORE]')

    books = [book.to_dict() for book in DB.collection('books').stream()]

    for book in books:
        Book.create(**book)

    print('[BOOKS GOT]')
    
    while True:
        time.sleep(3600)
        
        if datetime.datetime.now().hour == 0:
            print('[UPDATING TOKENS]')
            
            for token in Token.select():
                token.validate()
                
            print('[TOKENS UPDATED]')
            
            start = time.time()
                
            print('[UPLOADING DATA TO FIRESTORE]')
            
            books_collection = DB.collection('books')
            
            for book in Book.select():
                print(book.id)
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
