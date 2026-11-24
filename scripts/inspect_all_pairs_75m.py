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

close_pairs = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        p1, p2 = stops[i], stops[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 75.0:
            close_pairs.append((d, p1['name'], p2['name'], p1['monthly_boardings'], p2['monthly_boardings'], p1['corridor'], p2['corridor']))

close_pairs.sort(key=lambda x: x[0])
print(f"Total pairs within 75 meters: {len(close_pairs)}")
for i, c in enumerate(close_pairs):
    print(f"{i+1:2d}. {c[0]:5.1f}m: '{c[1]}' ({c[3]} pax) vs '{c[2]}' ({c[4]} pax)")
