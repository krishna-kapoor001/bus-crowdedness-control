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

hubs = [s for s in stops if s.get('is_major_hub', False)]

print(f"Total hubs: {len(hubs)}")

close_hubs = []
for i in range(len(hubs)):
    for j in range(i + 1, len(hubs)):
        h1, h2 = hubs[i], hubs[j]
        d = haversine(h1['latitude'], h1['longitude'], h2['latitude'], h2['longitude'])
        if d < 500:
            close_hubs.append((d, h1['name'], h2['name'], h1['latitude'], h1['longitude'], h2['latitude'], h2['longitude']))

close_hubs.sort(key=lambda x: x[0])
print(f"Hub pairs within 500m of each other: {len(close_hubs)}")
for c in close_hubs:
    print(f"  {c[0]:5.1f}m: '{c[1]}' vs '{c[2]}'")
