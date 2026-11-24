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
    profiles = json.load(f)

close_pairs = []
for i in range(len(profiles)):
    for j in range(i + 1, len(profiles)):
        p1 = profiles[i]
        p2 = profiles[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 60:
            close_pairs.append((d, p1['name'], p2['name']))

print(f"Total stops within 60 meters of each other: {len(close_pairs)}")
for d, n1, n2 in sorted(close_pairs):
    print(f"  {d:.1f}m: '{n1}' vs '{n2}'")
