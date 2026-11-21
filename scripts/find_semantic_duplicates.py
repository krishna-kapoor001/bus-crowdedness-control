import json, math, os, re
from collections import defaultdict
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def clean_name(name):
    s = name.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bgurudawara\b', 'gurudwara', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def name_sim(n1, n2):
    c1 = clean_name(n1)
    c2 = clean_name(n2)
    if c1 == c2: return 1.0
    if c1 in c2 or c2 in c1: return 0.9
    return SequenceMatcher(None, c1, c2).ratio()

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

semantic_duplicates = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 150:
            sim = name_sim(s1['name'], s2['name'])
            if sim >= 0.55:
                semantic_duplicates.append((d, sim, s1, s2))

semantic_duplicates.sort(key=lambda x: (x[0], -x[1]))
print(f"Found {len(semantic_duplicates)} semantic duplicate / near-duplicate pairs within 150m:")
for d, sim, s1, s2 in semantic_duplicates:
    print(f"  {d:.1f}m (sim {sim:.2f}): '{s1['name']}' <==> '{s2['name']}'")
