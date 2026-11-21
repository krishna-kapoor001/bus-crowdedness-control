import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/network/geojson"
with urllib.request.urlopen(url, timeout=5) as resp:
    data = json.loads(resp.read().decode('utf-8'))
    for f in data.get('features', []):
        name = f['properties']['name']
        if 'Shahdara' in name or 'Yamuna Vihar' in name:
            print(f"  {name} (is_hub={f['properties']['is_hub']}): {f['geometry']['coordinates']}")
