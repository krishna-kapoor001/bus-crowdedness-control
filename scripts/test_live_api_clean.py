import urllib.request
import json
import time

time.sleep(1)
with urllib.request.urlopen('http://localhost:8000/api/v1/network/geojson', timeout=5) as r:
    data = json.loads(r.read().decode())
    feats = data.get('features', [])
    hubs = [f for f in feats if f['properties'].get('is_hub')]
    print(f"Network GeoJSON: {len(feats)} features, {len(hubs)} Major Hubs (Black Dots)")

with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops', timeout=5) as r:
    stops = json.loads(r.read().decode())
    hubs = [s for s in stops if s.get('is_major_hub')]
    print(f"Journey stops: {len(stops)} stops, {len(hubs)} Major Hubs")
