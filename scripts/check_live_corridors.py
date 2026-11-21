import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/network/corridors'
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode('utf-8'))

for c in data:
    if c['id'] == 'corridor-airport':
        print(f"ID: {c['id']}")
        print(f"Name: {c['name']}")
        print(f"Stops: {c.get('stops')}")
        print(f"Coordinates count: {len(c.get('coordinates', []))}")
        print("Coordinates:", c.get('coordinates'))
