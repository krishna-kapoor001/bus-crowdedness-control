import json
import csv
import re
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Load official GTFS
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        gtfs_stops.append({
            'name': row['stop_name'],
            'lat': float(row['stop_lat']),
            'lon': float(row['stop_lon'])
        })

print(f"Auditing all {len(stops)} stops:")
# Classify stops
hubs = [s for s in stops if s.get('is_major_hub')]
regular = [s for s in stops if not s.get('is_major_hub')]

print(f"Total hubs: {len(hubs)}, Total regular: {len(regular)}")

# Check for any coordinates with precision < 4 decimals (e.g. 28.52, 77.18)
imprecise_hubs = []
for h in hubs:
    lat_str = str(h['latitude'])
    lon_str = str(h['longitude'])
    if len(lat_str.split('.')[-1]) < 4 or len(lon_str.split('.')[-1]) < 4:
        imprecise_hubs.append(h)

print(f"Imprecise hubs (< 4 decimals): {len(imprecise_hubs)}")
for h in imprecise_hubs:
    print(f"  HUB: '{h['name']}' -> ({h['latitude']}, {h['longitude']})")

imprecise_reg = []
for r in regular:
    lat_str = str(r['latitude'])
    lon_str = str(r['longitude'])
    if len(lat_str.split('.')[-1]) < 4 or len(lon_str.split('.')[-1]) < 4:
        imprecise_reg.append(r)

print(f"\nImprecise regular stops (< 4 decimals): {len(imprecise_reg)}")
for r in imprecise_reg[:30]:
    print(f"  REG: '{r['name']}' -> ({r['latitude']}, {r['longitude']})")
