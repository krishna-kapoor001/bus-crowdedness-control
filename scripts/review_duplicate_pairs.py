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

def normalize(name):
    s = name.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bterminal\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bmor\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bmore\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bchowk\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().lower()
    return s

def words_overlap(n1, n2):
    w1 = set(normalize(n1).split())
    w2 = set(normalize(n2).split())
    ignore = {'road', 'marg', 'block', 'phase', 'sec', 'sector', 'delhi', 'crossing', 'stand', 'stop', 'gate', 'near', 'opp', 'opposite'}
    w1_sig = w1 - ignore
    w2_sig = w2 - ignore
    if not w1_sig or not w2_sig:
        return 0.0
    intersection = w1_sig.intersection(w2_sig)
    return len(intersection) / min(len(w1_sig), len(w2_sig))

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open(os.path.join(DATA_DIR, 'osm_delhi_all_bus_stops.json'), 'r', encoding='utf-8') as f:
    osm_stops = json.load(f)
valid_osm = [s for s in osm_stops if isinstance(s.get('latitude'), (int, float)) and isinstance(s.get('longitude'), (int, float))]

pairs = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 180:
            norm1 = normalize(s1['name'])
            norm2 = normalize(s2['name'])
            sim = SequenceMatcher(None, norm1, norm2).ratio()
            overlap = words_overlap(s1['name'], s2['name'])
            if norm1 == norm2 or norm1 in norm2 or norm2 in norm1 or (overlap >= 0.8 and d <= 150) or (sim >= 0.70 and d <= 120):
                pairs.append((d, s1, s2))

pairs.sort(key=lambda x: x[0])
print(f"Total pairs to merge: {len(pairs)}")
for d, s1, s2 in pairs:
    print(f"\n[{d:.1f}m]")
    print(f"  A: '{s1['name']}' at ({s1['latitude']}, {s1['longitude']}) - Hub: {s1.get('is_major_hub', False)}")
    print(f"  B: '{s2['name']}' at ({s2['latitude']}, {s2['longitude']}) - Hub: {s2.get('is_major_hub', False)}")
