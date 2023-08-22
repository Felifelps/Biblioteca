'''
import random
n = [random.randint(33, 126) for i in range(15)]
print(''.join(map(lambda x: chr(x), n)))
'''
import secrets
print(secrets.token_hex())