print('STARTING APP')
from apibiblioteca import app
print('APP STARTED')
if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0')