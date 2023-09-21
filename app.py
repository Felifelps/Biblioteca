from api import User, Files, Book, Lending
from api.connector import Connector
import asyncio, json

def dump(dictionary):
    print(json.dumps(dictionary, indent=4))

async def main():
    '''
    a = await Book.new(
        'Mulheres sem sombra',
        'Silvia Tubert',
        'Editora Rosa dos Tempos',
        '1',
        '600',
        'Maternidade-Aspectos analíticos.2.Reprodução-Inovações tecnológicas',
        '4',
        '1'
    )
    '''
            
    dump(await Lending.new('2018125194-3', '20'))
    dump(await Lending.all(False))
    
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