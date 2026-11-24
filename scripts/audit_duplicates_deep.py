import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops in dataset: {len(stops)}")

# 1. Exact coordinate duplicates
coord_map = {}
for s in stops:
    k = (s['latitude'], s['longitude'])
    if k not in coord_map:
        coord_map[k] = []
    coord_map[k].append(s['name'])

exact_dup = {k: v for k, v in coord_map.items() if len(v) > 1}
print(f"Exact coordinate duplicates (0m): {len(exact_dup)}")
for k, v in exact_dup.items():
    print(f"  0m duplicate at {k}: {v}")

# 2. Pairs within 80 meters
pairs_80m = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        d = haversine(stops[i]['latitude'], stops[i]['longitude'], stops[j]['latitude'], stops[j]['longitude'])
        if d < 80:
            pairs_80m.append((stops[i], stops[j], d))

print(f"\nTotal pairs within 80m: {len(pairs_80m)}")
for s1, s2, d in sorted(pairs_80m, key=lambda x: x[2]):
    h1 = "STAND" if s1.get('is_major_hub') else "STOP"
    h2 = "STAND" if s2.get('is_major_hub') else "STOP"
    print(f"  {d:5.1f}m: [{h1:5s}] '{s1['name']}' <---> [{h2:5s}] '{s2['name']}'")
