from api import app
from json import dumps
from os import getenv, walk     
from os.path import abspath        
schema = {}
for root, dirs, files in walk('.'):
    if 'venv' in root or 'git' in root or '__pycache__' in root:
        continue
    schema[root] = files
    
print(abspath())

for dir, files in schema.items():
    if dir == '.':
        for file in files:
            print(file)
        continue
    print(dir.replace('.\\', '> '))
    for file in files:
        print('  ', file)
    

if __name__ == '__main__':
    app.run(port=getenv('PORT'))
