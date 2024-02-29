""" This module contains the 'watcher' function, which is 
responsible for validating tokens daily and for making 
requests to the API.

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
import time
import requests
from .models import Token


async def _watcher():
    """
    Asynchronous function that contains the main logic of the watcher script
    """

    print('[WATCHER STARTED]')

    # Infinite loop
    while True:
        # Auto requests every 10 minutes
        # Totalizing 1 hour
        counter = 0
        while counter < 6:
            print('[REQUESTING]')
            response = requests.post(
                'https://bibliotecamilagres-xll1.onrender.com/books/length',
                data={},
                timeout=1000
            )
            print(f'[REQUESTED {response.status_code}]')
            time.sleep(600)
            counter += 1

        # If the hour is 0
        if datetime.datetime.now().hour == 0:
            print('[UPDATING TOKENS]')

            # Loop through each token
            for token in Token.select():
                # Validate and update the token
                token.validate()

            print('[TOKENS UPDATED]')

def watcher():
    """
    Function that creates a new event loop,
    runs the _watcher() function in that loop,
    and starts the loop as a daemon thread
    """
    loop = new_event_loop()
    loop.run_until_complete(_watcher())


WATCHER = Thread(target=watcher, name='WATCHER', daemon=True)
