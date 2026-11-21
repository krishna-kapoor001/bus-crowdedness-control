import urllib.request
import urllib.parse
import json

queries = [
    "Shahdara Terminal, Delhi",
    "Shahdara Bus Terminal, Delhi",
    "Shahdara Terminal",
    "Shahdara Bus Stop",
    "DTC Bus Depot Yamuna Vihar"
]

headers = {'User-Agent': 'TransportDelhiResearch/1.0 (contact@transportdelhi.org)'}

for q in queries:
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(q)}&format=json&addressdetails=1&limit=5"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"=== Query: {q} ===")
            for item in data:
                print(f"  Name: {item.get('display_name')}")
                print(f"  Type: {item.get('type')}, Class: {item.get('class')}")
                print(f"  Lat: {item.get('lat')}, Lon: {item.get('lon')}")
                print(f"  OSM ID: {item.get('osm_type')} {item.get('osm_id')}")
    except Exception as e:
        print(f"Query {q} failed: {e}")
