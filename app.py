from api import User, Files, Book, Lending
from api.connector import Connector
import asyncio, json

def dump(*dicts):
    for i in dicts:
        if isinstance(i, list):
            dump(*i)
        else:
            try: 
                i = i.to_dict()
            except Exception as e:
                print(e)
            print(json.dumps(i, indent=4))

async def main():
    #print(Files.upload('modelo_dados.png', temp=False))
    print(Files.download('modelo_dados.png', 'model.png'))

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
#app.run(debug=True, host='0.0.0.0')

'''
    print(await User.new(
        '2018125194-6',
        'cavalo',
        '18/08/2006',
        'Brejo Santo',
        '63250000',
        '88 994426429',
        'Vila Fronteiro'
    ))
    '''
    #print(await User.all())
    #print(await User.delete('2018125194-6'))
    #print(await User.update('2018125194-6', tel_pessoal='55 88 994426429'))
    #print(await User.validate('2018125194-5'))