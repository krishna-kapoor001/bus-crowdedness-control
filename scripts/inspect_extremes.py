import json
import urllib.request
import urllib.parse
import time

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")

# Let's inspect coordinates distribution
lats = [s['latitude'] for s in stops]
lons = [s['longitude'] for s in stops]
print(f"Lat range: {min(lats):.4f} to {max(lats):.4f}")
print(f"Lon range: {min(lons):.4f} to {max(lons):.4f}")

# Check any stops that might have odd coordinates or outliers
for s in stops:
    lat, lon = s['latitude'], s['longitude']
    name = s['name']
    # Check if too close to border or odd
    if lat > 28.85 or lat < 28.45 or lon < 76.90 or lon > 77.35:
        print(f"EDGE STOP: '{name}' at ({lat}, {lon}) - {s.get('corridor')}")
