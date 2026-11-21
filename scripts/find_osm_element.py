import urllib.request
import urllib.parse
import json

query = """[out:json][timeout:25];
(
  node["name"~"Shahdara"](28.66, 77.27, 28.69, 77.30);
  way["name"~"Shahdara"](28.66, 77.27, 28.69, 77.30);
  node["amenity"="bus_station"](28.66, 77.27, 28.69, 77.30);
  way["amenity"="bus_station"](28.66, 77.27, 28.69, 77.30);
);
out center;
"""

url = "https://overpass-api.de/api/interpreter"
req = urllib.request.Request(url, data=query.encode('utf-8'), headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Total elements found: {len(data.get('elements', []))}")
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            name = tags.get('name', '')
            amenity = tags.get('amenity', '')
            highway = tags.get('highway', '')
            if 'bus' in name.lower() or 'terminal' in name.lower() or amenity == 'bus_station' or highway == 'bus_stop':
                print(f"TYPE: {el.get('type')}, ID: {el.get('id')}, NAME: {name}, AMENITY: {amenity}, HW: {highway}, LAT: {lat}, LON: {lon}")
except Exception as e:
    print("Error:", e)
