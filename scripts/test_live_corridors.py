import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/network/corridors'
with urllib.request.urlopen(url) as resp:
    headers = dict(resp.getheaders())
    print("Cache-Control header:", headers.get('cache-control'))
    data = json.loads(resp.read().decode('utf-8'))

print(f"Total corridors returned: {len(data)}")
for c in data:
    if c['id'] == 'corridor-airport':
        print(f"Airport corridor stops count: {len(c['stops'])}")
        print(f"Airport corridor coordinates count: {len(c['coordinates'])}")
        print(f"First coord: {c['coordinates'][0]}")
        print(f"Last coord: {c['coordinates'][-1]}")
