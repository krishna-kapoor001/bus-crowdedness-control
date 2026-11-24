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
non_hubs = [s for s in stops if not s.get('is_major_hub')]

print(f"Hubs: {len(hubs)}, Non-hubs: {len(non_hubs)}")

for h in hubs:
    th = tokens(h['name'])
    for nh in non_hubs:
        tnh = tokens(nh['name'])
        d = haversine(h['latitude'], h['longitude'], nh['latitude'], nh['longitude'])
        if th and tnh and th == tnh and d < 600:
            print(f"DUPLICATE REGULAR STOP NEAR HUB ({d:.1f}m): Hub '{h['name']}' <---> Regular Stop '{nh['name']}'")
        elif th and tnh and (th.issubset(tnh) or tnh.issubset(th)) and d < 150:
            print(f"VERY CLOSE OVERLAP ({d:.1f}m): Hub '{h['name']}' <---> Regular Stop '{nh['name']}'")
