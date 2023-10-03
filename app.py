from api import app
from api.keys import Keys
from api.book import Book
from api.connector import Connector
from api.lending import Lending
from api.user import User
import asyncio, json

#TODO: Fazer a documentação geral usando sphinx

def dump(*dicts):
    for i in dicts:
        if isinstance(i, list):
            dump(*i)
        else:
            try: 
                i = i.to_dict()
            except Exception as e:
                pass
            print(json.dumps(i, indent=4))

async def main():
    pass
    
import os 
os.environ['QUART_ENV'] = 'development'
loop = asyncio.new_event_loop()
app.run(debug=True, host='0.0.0.0', loop=loop, use_reloader=True)
