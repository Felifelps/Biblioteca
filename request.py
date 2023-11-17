import time, requests, threading, random
url='https://apibiblioteca.2.ie-1.fl0.io/book/new'
#url='http://192.168.0.198:8080/book/new'
for i in range(0, 500):
    threading.Thread(target=lambda: print(i, requests.post(url=url, json={
        "key": 'f1563cb61eaf857ce3042c12cd94e774',
        "CDD": str(random.randint(100, 1000)),
        "prateleira": str(random.randint(1, 10)),
        "editora": str(random.randbytes(20)),
        "edicao": str(random.randbytes(20)),
        "titulo": f"Mil exemplares {i}",
        "assuntos": str(random.randbytes(20)),
        "estante": str(random.randint(1, 50)),
        "autor": str(random.randbytes(20))
    }).text)).start()
    