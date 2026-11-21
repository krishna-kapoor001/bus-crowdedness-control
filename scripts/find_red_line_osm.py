import urllib.request
import json

# Search for Delhi Metro Red Line around Shahdara:
query = """[out:json][timeout:25];
(
  way["name"~"Red Line"](28.665, 77.275, 28.685, 77.30);
  way["railway"](28.665, 77.275, 28.685, 77.30);
);
out center;
"""

url = "https://overpass-api.de/api/interpreter"
req = urllib.request.Request(url, data=query.encode('utf-8'), headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print(f"Elements: {len(data.get('elements', []))}")
        for el in data.get('elements', []):
            tags = el.get('tags', {})
            lat = el.get('lat') or el.get('center', {}).get('lat')
            lon = el.get('lon') or el.get('center', {}).get('lon')
            print(f"Way {el.get('id')}: {tags.get('name')} {tags.get('railway')} center=({lat}, {lon})")
except Exception as e:
    print("Error:", e)
