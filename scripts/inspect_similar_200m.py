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

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

similar_pairs = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        p1, p2 = stops[i], stops[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 200.0:
            t1 = set(re.findall(r'[a-zA-Z]+', p1['name'].lower()))
            t2 = set(re.findall(r'[a-zA-Z]+', p2['name'].lower()))
            ignore = {'bus', 'stop', 'stand', 'crossing', 'terminal', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'block', 'phase', 'sec', 'sector', 'depot', 'isbt'}
            overlap = (t1 & t2) - ignore
            if len(overlap) >= 1:
                similar_pairs.append((d, p1['name'], p2['name'], list(overlap), p1['monthly_boardings'], p2['monthly_boardings']))

similar_pairs.sort(key=lambda x: x[0])
print(f"Total similar-name pairs within 200m: {len(similar_pairs)}")
for i, c in enumerate(similar_pairs):
    print(f"{i+1:2d}. {c[0]:5.1f}m: '{c[1]}' vs '{c[2]}' (common: {c[3]})")
