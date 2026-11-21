import urllib.request
import json

# Fetch way 683662846 and way 351420747 from OSM API directly:
urls = [
    ("way 683662846 (bus_station)", "https://api.openstreetmap.org/api/0.6/way/683662846/full.json"),
    ("way 351420747 (information)", "https://api.openstreetmap.org/api/0.6/way/351420747/full.json")
]

headers = {'User-Agent': 'TransportDelhiResearch/1.0'}

for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            print(f"=== {name} ===")
            nodes = [el for el in data.get('elements', []) if el.get('type') == 'node']
            lats = [n['lat'] for n in nodes]
            lons = [n['lon'] for n in nodes]
            print(f"  Nodes count: {len(nodes)}")
            print(f"  Lat range: {min(lats)} to {max(lats)}, Center: {sum(lats)/len(lats)}")
            print(f"  Lon range: {min(lons)} to {max(lons)}, Center: {sum(lons)/len(lons)}")
            for el in data.get('elements', []):
                if el.get('type') == 'way':
                    print(f"  Tags: {el.get('tags')}")
    except Exception as e:
        print(f"Error {name}: {e}")
