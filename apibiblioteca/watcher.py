from asyncio import new_event_loop
from .utils import DB
from .models import db, Token, Book, model_to_dict
import requests
from threading import Thread
import time


async def _watcher():
    print('[WATCHER STARTED]')

    print('[GETTING BOOKS FROM FIRESTORE]')
    
    for doc in DB.collection('books').stream():
        Book.create(**doc.to_dict())
        
    print('[BOOKS GOT]')

    while True:
        start = time.time()

        print('[UPDATING TOKENS]')
        
        for token in Token.select():
            token.validate()
            
        print('[TOKENS UPDATED]')
            
        print('[UPLOADING DATA TO FIRESTORE]')
        
        books_collection = DB.collection('books')
        for book in Book.select():
            books_collection.document(str(book.id)).set(model_to_dict(book))
            
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
