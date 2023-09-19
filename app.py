from api import User, Files, Book
import asyncio

async def main():
    '''
    print(await User().new(
        '2018125194-4',
        'Felipe',
        '18/08/2006',
        'Brejo Santo',
        '63250000',
        '88 994426429',
        'Vila Fronteiro'
    ))
    '''
    print(await User().all())
    print(await User().delete('2018125194-4'))
    print(await User().all())
    #print(await User().get('2018125194-3'))
    

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
#app.run(debug=True, host='0.0.0.0')