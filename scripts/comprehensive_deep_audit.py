import json
import math
import re
from difflib import SequenceMatcher

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops to audit: {len(stops)}")

# 1. Spatial Bounds Check (Delhi NCT + Immediate NCR Border Terminals)
# Delhi NCT bounding box: Lat 28.40 to 28.90, Lon 76.80 to 77.40
out_of_bounds = []
for s in stops:
    lat, lon = s['latitude'], s['longitude']
    if not (28.40 <= lat <= 28.92 and 76.80 <= lon <= 77.45):
        out_of_bounds.append((s['name'], lat, lon))

print(f"\n[1] Out of Bounds Stops: {len(out_of_bounds)}")
for o in out_of_bounds:
    print(f"  {o[0]}: lat={o[1]}, lon={o[2]}")

# 2. Check Bus Stands & Terminals Ground Truth Alignment
HUB_KEYWORDS = ['terminal', 'isbt', 'depot', 'bus stand']
terminals = [s for s in stops if any(k in s['name'].lower() for k in HUB_KEYWORDS)]
print(f"\n[2] Total Terminals / Depots / Stands in Dataset: {len(terminals)}")
unflagged_terminals = [t['name'] for t in terminals if not t.get('is_major_hub')]
print(f"  Terminals not flagged as is_major_hub: {len(unflagged_terminals)}")
for ut in unflagged_terminals[:15]:
    print(f"    '{ut}'")

# 3. Check Duplicate Pairs within 150 meters that share key words or semantics
def clean_tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', name.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'road', 'delhi', 'village'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

nearby_similar = []
for i in range(len(stops)):
    s1 = stops[i]
    t1 = clean_tokens(s1['name'])
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 180:
            t2 = clean_tokens(s2['name'])
            overlap = t1 & t2
            # Also calculate string similarity
            c1 = re.sub(r'[^a-z0-9]', '', s1['name'].lower())
            c2 = re.sub(r'[^a-z0-9]', '', s2['name'].lower())
            sim = SequenceMatcher(None, c1, c2).ratio()
            
            # If they share primary tokens or have high similarity, or if distance is very small (< 45m)
            if overlap or sim >= 0.65 or d < 45:
                nearby_similar.append({
                    'stop1': s1['name'],
                    'stop2': s2['name'],
                    'dist': round(d, 1),
                    'overlap': list(overlap),
                    'sim': round(sim, 2),
                    'hub1': s1.get('is_major_hub', False),
                    'hub2': s2.get('is_major_hub', False),
                    'boardings1': s1.get('monthly_boardings', 0),
                    'boardings2': s2.get('monthly_boardings', 0),
                    'lat1': s1['latitude'],
                    'lon1': s1['longitude'],
                    'lat2': s2['latitude'],
                    'lon2': s2['longitude'],
                })

nearby_similar.sort(key=lambda x: x['dist'])
print(f"\n[3] Nearby / Similar Pairs within 180m: {len(nearby_similar)}")
for item in nearby_similar:
    print(f"  {item['dist']:5.1f}m: '{item['stop1']}' <---> '{item['stop2']}' | overlap: {item['overlap']} (sim={item['sim']})")
