import requests

res = requests.get('http://127.0.0.1:5000/articles/2024-05-18T19:11:35.000Z/2024-05-20T20:11:35.000Z/3')
print(res.json())