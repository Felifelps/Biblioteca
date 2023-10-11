from api import app
from os import getenv              

if __name__ == '__main__':
    app.run(port=getenv('PORT'))
