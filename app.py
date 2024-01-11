from apibiblioteca import app, WATCHER, utils, Book

print('[GETTING BOOKS FROM FIRESTORE]')
    
for doc in utils.DB.collection('books').stream():
    data = doc.to_dict()
    data.pop('id')
    Book.create(**data)
    
print('[BOOKS GOT]')

WATCHER.start()

if __name__ == '__main__':
    app.run(port=8080, host='0.0.0.0', debug=True)
