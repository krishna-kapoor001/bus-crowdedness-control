import urllib.request
import json

overpass_url = 'https://overpass-api.de/api/interpreter'
query = """[out:json][timeout:20];
(
  node["amenity"="bus_station"](28.40,76.84,28.90,77.40);
  way["amenity"="bus_station"](28.40,76.84,28.90,77.40);
  node["public_transport"="station"](28.40,76.84,28.90,77.40);
  node["highway"="bus_stop"]["name"](28.40,76.84,28.90,77.40);
);
out center tags;"""

try:
    req = urllib.request.Request(overpass_url, data=query.encode('utf-8'), headers={'User-Agent': 'TransportDelhiBBox/1.0'})
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read().decode())
        elements = data.get('elements', [])
        print(f"Retrieved {len(elements)} official bus stops/stations from OSM bbox!")
        with open('data/osm_delhi_stations.json', 'w', encoding='utf-8') as f:
            json.dump(elements, f, indent=2)
except Exception as e:
    print('Error:', e)
