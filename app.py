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
    
    dump(await User.new(
        '2018125194-2', 
        'cavalo',
        '18/08/2006',
        'Brejo Santo',
        'felipefelipe23456@gmail.com',
        '63250000',
        '88 994426429',
        'Vila Fronteiro'
    ))
    
    #dump(
    #    await User.query()
    #)
    book = await Book.new(
        'pokemon',
        'joel',
        'editora brasil',
        '1°',
        '666',
        'Pokemon',
        '1',
        '2'
    )'''
    print(await User.query('RG', '==', '20181221'))
    
    
    
    
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