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
    #await Keys.delete('felipefelipe23456@gmail.com')
    #print(await Keys.register_new_key('felipefelipe23456@gmail.com'))
    #await Keys.validate('felipefelipe23456@gmail.com')
    #print(await Keys.get('felipefelipe23456@gmail.com'))
    print(await Keys.check_key('felipefelipe23456@gmail.com', "7ad39792b2868af121b230296a99d693"))
    return 
    
    
loop = asyncio.new_event_loop()
loop.run_until_complete(app.run(debug=True, host='0.0.0.0', use_reloader=True, loop=loop))
