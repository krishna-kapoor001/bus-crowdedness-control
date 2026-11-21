import urllib.request
import urllib.parse
import json

overpass_url = 'https://overpass.private.coffee/api/interpreter'
# Query bus stops or bus stations in Yamuna Vihar box: 28.69, 77.26, 28.71, 77.28
query = """
[out:json][timeout:25];
(
  node["highway"="bus_stop"](28.69,77.26,28.71,77.28);
  node["amenity"="bus_station"](28.69,77.26,28.71,77.28);
  way["amenity"="bus_station"](28.69,77.26,28.71,77.28);
  way["landuse"="depot"](28.69,77.26,28.71,77.28);
  node["public_transport"](28.69,77.26,28.71,77.28);
);
out center;
"""

req = urllib.request.Request(
    overpass_url,
    data=urllib.parse.urlencode({'data': query}).encode('utf-8'),
    headers={'User-Agent': 'TransportDelhiBot/1.0'}
)

try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        elements = data.get('elements', [])
        print(f"Total elements in Yamuna Vihar box: {len(elements)}")
        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name', tags.get('name:en', 'Unnamed'))
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            print(f"  OSM Element: '{name}' | Tags: {tags.get('highway') or tags.get('amenity') or tags.get('public_transport')} | ({lat}, {lon})")
except Exception as e:
    print("Error:", e)
