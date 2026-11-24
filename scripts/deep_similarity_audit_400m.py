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

def clean_toks(s):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', s.lower())
    ignore = {'bus', 'stop', 'stand', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'block', 'phase', 'sec', 'sector', 'depot', 'isbt', 'terminal', 'colony', 'near', 'opp', 'opposite'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total current stops: {len(stops)}")

# Find all pairs within 350m that share a significant token or have string similarity > 0.65
suspects = []
for i in range(len(stops)):
    for j in range(i + 1, len(stops)):
        p1, p2 = stops[i], stops[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 350.0:
            t1 = clean_toks(p1['name'])
            t2 = clean_toks(p2['name'])
            overlap = t1 & t2
            sim = SequenceMatcher(None, p1['name'].lower(), p2['name'].lower()).ratio()
            if overlap or sim > 0.60:
                suspects.append((d, p1['name'], p2['name'], list(overlap), sim, p1['monthly_boardings'], p2['monthly_boardings']))

suspects.sort(key=lambda x: x[0])
print(f"Total suspect pairs within 350m: {len(suspects)}")
for i, s in enumerate(suspects):
    print(f"{i+1:2d}. {s[0]:5.1f}m: '{s[1]}' ({s[5]} pax) vs '{s[2]}' ({s[6]} pax) | Overlap: {s[3]} | Sim: {s[4]:.2f}")
