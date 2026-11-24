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

def clean_str(s):
    s = s.lower()
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

fuzzy_dups = []
for i in range(len(stops)):
    s1 = stops[i]
    c1 = clean_str(s1['name'])
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        c2 = clean_str(s2['name'])
        ratio = SequenceMatcher(None, c1, c2).ratio()
        if ratio >= 0.75:
            d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
            if d < 350: # Within 350 meters
                fuzzy_dups.append((s1['name'], s2['name'], d, ratio))

fuzzy_dups.sort(key=lambda x: x[2])
print(f"Total fuzzy duplicate pairs within 350m (ratio >= 75%): {len(fuzzy_dups)}")
for s1, s2, d, r in fuzzy_dups:
    print(f"  {d:5.1f}m ({r*100:.0f}% match): '{s1}' <---> '{s2}'")
