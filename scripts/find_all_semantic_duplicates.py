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
    # remove common stop words
    ignore = {'road', 'marg', 'block', 'phase', 'sec', 'sector', 'delhi', 'crossing', 'stand', 'stop', 'gate', 'near', 'opp', 'opposite'}
    w1_sig = w1 - ignore
    w2_sig = w2 - ignore
    if not w1_sig or not w2_sig:
        return 0.0
    intersection = w1_sig.intersection(w2_sig)
    return len(intersection) / min(len(w1_sig), len(w2_sig))

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")

duplicates_to_merge = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        
        # Check if within 180m and significant word overlap or string similarity
        if d <= 180:
            norm1 = normalize(s1['name'])
            norm2 = normalize(s2['name'])
            sim = SequenceMatcher(None, norm1, norm2).ratio()
            overlap = words_overlap(s1['name'], s2['name'])
            
            # Condition for being the same transit stop:
            # 1. Exact normalized match within 180m
            # 2. Or overlap >= 0.8 within 150m
            # 3. Or string similarity >= 0.65 within 120m
            # 4. Or one is substring of other within 120m
            is_dup = False
            reason = ""
            if norm1 == norm2:
                is_dup = True
                reason = "exact normalized match"
            elif norm1 in norm2 or norm2 in norm1:
                is_dup = True
                reason = "substring match"
            elif overlap >= 0.8 and d <= 150:
                is_dup = True
                reason = f"word overlap {overlap:.2f}"
            elif sim >= 0.70 and d <= 120:
                is_dup = True
                reason = f"high similarity {sim:.2f}"
                
            if is_dup:
                duplicates_to_merge.append({
                    'distance': d,
                    'stop1': s1,
                    'stop2': s2,
                    'reason': reason
                })

duplicates_to_merge.sort(key=lambda x: x['distance'])
print(f"\nIDENTIFIED {len(duplicates_to_merge)} CONFIRMED DUPLICATE PAIRS TO MERGE:")
for item in duplicates_to_merge:
    d = item['distance']
    s1 = item['stop1']
    s2 = item['stop2']
    print(f"  [{d:.1f}m] '{s1['name']}' <==> '{s2['name']}' ({item['reason']})")
