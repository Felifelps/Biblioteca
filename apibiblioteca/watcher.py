""" This module contains the watcher script which is responsible for:

- Periodically fetching books data from a Firestore database and
storing it in a local SQLite database.

- Validating and updating token records in the
local SQLite database.

- Uploading the latest books data from the local SQLite
database to the Firestore database.

The watcher script runs as a daemon thread and is started by
invoking the watcher() function.

Functions:
_watcher(): An asynchronous function that contains the
main logic of the watcher script.

watcher(): A function that creates a new event loop,
runs the _watcher() function in that loop, and starts
the loop as a daemon thread.

"""


from asyncio import new_event_loop
from threading import Thread
import datetime
import os
import time
import requests
from playhouse.shortcuts import model_to_dict
from .utils import DB
from .models import (
    Token,
    Book
)


async def _watcher():
    """
    Asynchronous function that contains the main logic of the watcher script
    """

    print('[WATCHER STARTED]')

    if not os.path.exists("database.db"):

        print(len(list(Book.select())))

        # Checks if the database is empty
        if len(list(Book.select())) == 0:

            print('[GETTING BOOKS FROM FIRESTORE]')

            # Fetching books data from Firestore
            books = [book.to_dict() for book in DB.collection('books').stream()]

            # Loop through each book
            for book in books:
                # Create a new book record in the local SQLite database
                Book.create(**book)

            print('[BOOKS GOT]')

    # Infinite loop
    while True:
        # Auto requests every 10 minutes
        # Totalizing 1 hour
        for i in range(6):
            print('[REQUESTING]')
            response = requests.post(
                'https://bibliotecamilagres-xll1.onrender.com/books/length',
                data={},
                timeout=1000
            )
            print('[REQUESTED', response.status_code, ']')
            time.sleep(600)

        # If the hour is 0
        if datetime.datetime.now().hour == 0:
            print('[UPDATING TOKENS]')

            # Loop through each token
            for token in Token.select():
                # Validate and update the token
                token.validate()

            print('[TOKENS UPDATED]')

            # Measure the time taken to upload the data to Firestore
            start = time.time()

            print('[UPLOADING DATA TO FIRESTORE]')

            # Get the books collection from Firestore
            books_collection = DB.collection('books')

            # Loop through each book in the local SQLite database
            for book in Book.select():
                print(book.id)
                try:
                    # Upload the book data to Firestore
                    books_collection.document(
                        str(book.id)
                    ).set(model_to_dict(book))
                except Exception as e:
                    print(e)
                    break

            message = (
                '[DATA UPLOADED TO FIRESTORE IN',
                str(time.time() - start)[:4],
                'SECONDS]'
            )

            print(*message)


def watcher():
    """
    Function that creates a new event loop,
    runs the _watcher() function in that loop,
    and starts the loop as a daemon thread
    """
    loop = new_event_loop()
    loop.run_until_complete(_watcher())


WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)
