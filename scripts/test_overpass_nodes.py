import urllib.request
import urllib.parse
import json

overpass_url = "https://overpass-api.de/api/interpreter"
query = """
[out:json][timeout:60];
area["ISO3166-2"="IN-DL"]->.delhi;
node["amenity"="bus_station"](area.delhi);
out;
"""

req = urllib.request.Request(
    overpass_url,
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'TransportDelhiApp/1.0'}
)

try:
    with urllib.request.urlopen(req, timeout=40) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        elements = data.get('elements', [])
        print(f"Total bus_station nodes in Delhi: {len(elements)}")
        for el in elements[:10]:
            print(el.get('tags', {}).get('name'), el.get('lat'), el.get('lon'))
        with open('data/osm_bus_stations_nodes.json', 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2)
except Exception as e:
    print("Error:", e)
