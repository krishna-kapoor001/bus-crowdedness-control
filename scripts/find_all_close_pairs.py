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

close_pairs = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        s1 = stops[i]
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 50.0:
            close_pairs.append((d, s1['name'], s2['name'], s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude']))

close_pairs.sort()
print(f"Total pairs within 50m: {len(close_pairs)}")
for d, n1, n2, lat1, lon1, lat2, lon2 in close_pairs:
    print(f"  d={d:.1f}m: '{n1}' vs '{n2}' at ({lat1}, {lon1}) vs ({lat2}, {lon2})")
