import urllib.request
import urllib.parse
import json

overpass_url = "https://overpass-api.de/api/interpreter"
# Bounding box for Delhi NCT: 28.40, 76.84, 28.88, 77.38
query = """
[out:json][timeout:25];
(
  node["amenity"="bus_station"](28.40,76.84,28.88,77.38);
  way["amenity"="bus_station"](28.40,76.84,28.88,77.38);
  relation["amenity"="bus_station"](28.40,76.84,28.88,77.38);
);
out center;
"""

req = urllib.request.Request(
    overpass_url,
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'TransportDelhiBot/1.0'}
)

try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        elements = data.get('elements', [])
        print(f"Total bus stations found in Delhi OSM: {len(elements)}")
        for el in elements[:15]:
            tags = el.get('tags', {})
            name = tags.get('name', tags.get('name:en', 'Unnamed'))
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            print(f"  OSM Bus Station: '{name}' -> ({lat}, {lon})")
        # Save all to file for processing
        with open('data/osm_delhi_bus_stations.json', 'w', encoding='utf-8') as out:
            json.dump(elements, out, indent=2)
        print("Saved to data/osm_delhi_bus_stations.json")
except Exception as e:
    print("Error:", e)
