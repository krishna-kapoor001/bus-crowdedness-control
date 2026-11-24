import json
import re
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', name.lower())
    ignore = {'isbt', 'terminal', 'depot', 'cluster', 'bus', 'stand', 'stop', 'village', 'dtc'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
print(f"Total hubs: {len(hubs)}")

for i in range(len(hubs)):
    t1 = tokens(hubs[i]['name'])
    for j in range(i + 1, len(hubs)):
        t2 = tokens(hubs[j]['name'])
        d = haversine(hubs[i]['latitude'], hubs[i]['longitude'], hubs[j]['latitude'], hubs[j]['longitude'])
        if t1 and t2 and t1 == t2:
            print(f"EXACT DUPLICATE HUB ({d:.1f}m): '{hubs[i]['name']}' <---> '{hubs[j]['name']}'")
        elif t1 and t2 and (t1.issubset(t2) or t2.issubset(t1)) and d < 1200:
            print(f"CLOSE OVERLAPPING HUB ({d:.1f}m): '{hubs[i]['name']}' <---> '{hubs[j]['name']}'")
