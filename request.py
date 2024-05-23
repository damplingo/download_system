import requests

res = requests.get('http://127.0.0.1:5000/articles/2024-05-23T06:08:24.000Z/2')
res_2 = requests.get('http://127.0.0.1:5000/authors/gov0run')
res_3 = requests.get('http://127.0.0.1:5000/articles/2024-05-23T06:08:24.000Z/2024-05-23T13:08:24.000Z/2')
print(res_3.json())