import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/network/geojson'
req = urllib.request.Request(url)
with urllib.request.urlopen(req, timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8'))

features = data.get('features', [])
print(f"Live GeoJSON features count: {len(features)}")

yv_features = [f for f in features if 'yamuna vihar' in f['properties']['name'].lower()]
print(f"Yamuna Vihar features ({len(yv_features)}):")
for f in yv_features:
    p = f['properties']
    c = f['geometry']['coordinates']
    print(f"  - {p['name']}: lon={c[0]}, lat={c[1]}, is_hub={p['is_hub']}")
