import json
import math
import re

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', name.lower())
    return set(w for w in clean.split() if len(w) > 2 and w not in {'bus', 'stop', 'stand', 'terminal', 'crossing', 'more', 'road', 'delhi', 'village', 'block', 'phase', 'sec', 'sector', 'depot'})

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

similar_pairs = []
for i in range(len(stops)):
    t1 = tokens(stops[i]['name'])
    if not t1:
        continue
    for j in range(i + 1, len(stops)):
        t2 = tokens(stops[j]['name'])
        overlap = t1 & t2
        if overlap:
            d = haversine(stops[i]['latitude'], stops[i]['longitude'], stops[j]['latitude'], stops[j]['longitude'])
            if d < 120:
                similar_pairs.append((stops[i], stops[j], d, overlap))

similar_pairs.sort(key=lambda x: x[2])
print(f"Total similar name pairs within 120m: {len(similar_pairs)}")
for s1, s2, d, ov in similar_pairs:
    print(f"  {d:5.1f}m: '{s1['name']}' <---> '{s2['name']}' (shared: {ov})")
