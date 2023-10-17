import os 
for i, dirnames, filenames in os.walk():
    print(dirnames, filenames)
    break 

from apibiblioteca.api import app

app.run(port=8080, host='0.0.0.0')