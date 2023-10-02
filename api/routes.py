from api.book import Book
from api.email import Email
from api.files import Files
from api.lending import Lending
from api.user import User
from quart import request, Quart

app = Quart('Biblioteca')

import time
@app.route('/')
async def main():
    s = time.time()
    data = []
    data.append(
        await User.query('nome', '==', 'cavalo')   
    )
    return str(time.time() - s)
