from api import app, User, Email, Files, Book, Lending
from api.connector import Connector
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
                print(e)
            print(json.dumps(i, indent=4))

async def main():
    html = """
    <form method='GET' action="http://192.168.0.197:5000" style="text-align: center">
        <label for="name">Mande uma mensagem</label>
        <input type="text" name="msg" id="msg" placeholder="Mensagem aqui">
        <br>
        <br>
        <input type="submit">
    </form>
    """
    await Email.message('adryancaetano871@gmail.com', 'POkemon', html)
    
#loop = asyncio.new_event_loop()
#loop.run_until_complete(main())
app.run(debug=True, host='0.0.0.0')
