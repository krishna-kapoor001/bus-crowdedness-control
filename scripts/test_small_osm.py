import urllib.request
import urllib.parse
import json

# Test fetching bus stops in central Delhi: 28.60 to 28.65, 77.20 to 77.25
query = """
[out:json][timeout:15];
node["highway"="bus_stop"](28.62,77.20,28.64,77.22);
out body;
"""
url = 'https://overpass.private.coffee/api/interpreter'
req = urllib.request.Request(
    url,
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'TransportDelhiBot/1.0'}
)
try:
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode('utf-8'))
        elements = res.get('elements', [])
        print(f"Success! Found {len(elements)} OSM bus stops in slice!")
        for el in elements[:5]:
            print(f"  - {el.get('tags', {}).get('name')}: ({el['lat']}, {el['lon']})")
except Exception as e:
    print("Error:", e)
