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

similar_close = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        p1, p2 = stops[i], stops[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 100:
            t1 = set(re.findall(r'[a-zA-Z]+', p1['name'].lower()))
            t2 = set(re.findall(r'[a-zA-Z]+', p2['name'].lower()))
            ignore = {'bus', 'stop', 'stand', 'crossing', 'terminal', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'block', 'phase', 'sec', 'sector'}
            overlap = (t1 & t2) - ignore
            if len(overlap) >= 1:
                similar_close.append((d, p1['name'], p2['name'], list(overlap)))

similar_close.sort(key=lambda x: x[0])
print(f"Total similar-name stops within 100m: {len(similar_close)}")
for sc in similar_close:
    print(f"  {sc[0]:.1f}m: '{sc[1]}' vs '{sc[2]}' (common: {sc[3]})")
