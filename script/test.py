import requests

hash_name = 'Astral Drift'
base = 'https://www.c5game.com/dota.html?min=&max=&k='
response = requests.get(base + str(hash_name))
if response.status_code == 200:
    html = response.text
    print(html)
