import json
import re
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi, dlam = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")

def clean_base_name(name):
    n = re.sub(r'\s*\([0-9A-Za-z]+\)\s*', ' ', name)
    n = re.sub(r'\s*xing\b', ' Crossing', n, flags=re.IGNORECASE)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

base_map = {}
for s in stops:
    bn = clean_base_name(s['name']).lower()
    if bn not in base_map:
        base_map[bn] = []
    base_map[bn].append(s)

multiples = {k: v for k, v in base_map.items() if len(v) > 1}
print(f"Base name clusters with >1 stops: {len(multiples)}")
total_multi_stops = sum(len(v) for v in multiples.values())
print(f"Total stops belonging to multiple clusters: {total_multi_stops}")

print("\nSample 15 clusters:")
for k, v in list(multiples.items())[:15]:
    names = [s['name'] for s in v]
    dist = haversine(v[0]['latitude'], v[0]['longitude'], v[1]['latitude'], v[1]['longitude'])
    print(f"  Cluster '{k}': {names} -> dist: {dist:.1f}m")
