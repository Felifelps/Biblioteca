import time, requests
url='https://apibiblioteca.2.ie-1.fl0.io/book/new'
url='http://192.168.0.198:8080/book/new'
for i in range(1000):
    response = requests.post(url=url, json={
        "key": 'f1563cb61eaf857ce3042c12cd94e774',
        "CDD": "800",
        "prateleira": "1",
        "editora": "teste",
        "edicao": "teste",
        "titulo": f"Mil exemplares {i}",
        "assuntos": "1.Mais de mil exemplares",
        "estante": "2",
        "autor": "Felipe"
    })
    print(i, response.text)
    time.sleep(5)