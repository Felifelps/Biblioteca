from api import app
from api.data_handler import DataHandler
import asyncio

async def main():
    '''
    await DataHandler().new_user(
        RG='2018125194-3',
        nome='Felipe dos Santos Ferreira',
        data_nascimento='18/08/20060',
        local_nascimento='Brejo Santo, Ceará, Brasil',
        CEP=63250000,
        tel_pessoal='55 88 994426429',
        residencia='Vila Fronteiro'
    )
    
    await DataHandler().delete_user('2018125194-3')
    '''
    

#loop = asyncio.new_event_loop()
#loop.run_until_complete(main())
app.run(debug=True, host='0.0.0.0')