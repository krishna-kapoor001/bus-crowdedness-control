import os, sys, json, math, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

from scripts.deploy_osm_tile_perfect_stops import OSM_TILE_PINS

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def normalize_spelling(s):
    s = s.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bgurudawara\b', 'gurudwara', s, flags=re.IGNORECASE)
    s = re.sub(r'\bsarover\b', 'sarovar', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def canonical_key(s):
    c = normalize_spelling(s).lower()
    return re.sub(r'[^a-z0-9]', '', c)

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Group by canonical key
groups = defaultdict(list)
for s in stops:
    k = canonical_key(s['name'])
    groups[k].append(s)

stage1 = []
for k, group in groups.items():
    is_hub = any(s['is_major_hub'] for s in group)
    # Check if authoritative OSM tile pin matches
    matched_pin = None
    if k in OSM_TILE_PINS:
        matched_pin = OSM_TILE_PINS[k]
    else:
        for s in group:
            sk = re.sub(r'[^a-z0-9]', '', s['name'].lower())
            if sk in OSM_TILE_PINS:
                matched_pin = OSM_TILE_PINS[sk]
                break
                
    if matched_pin:
        lat, lon, is_h = matched_pin
        if is_h: is_hub = True
        # Pick cleanest name
        clean_name = sorted(group, key=lambda x: ('(' in x['name'], len(x['name'])))[0]['name']
        clean_name = re.sub(r'\(.*?\)', '', clean_name).strip()
        stage1.append({
            'name': clean_name,
            'latitude': lat,
            'longitude': lon,
            'is_major_hub': is_hub,
            'corridor': group[0].get('corridor', 'Delhi Transit Region')
        })
    elif len(group) == 1:
        s = group[0]
        cname = re.sub(r'\(.*?\)', '', s['name']).strip()
        stage1.append({
            'name': cname,
            'latitude': s['latitude'],
            'longitude': s['longitude'],
            'is_major_hub': s['is_major_hub'],
            'corridor': s.get('corridor', 'Delhi Transit Region')
        })
    else:
        # Cluster within 400m
        clusters = []
        for s in group:
            placed = False
            for c in clusters:
                c_lat = sum(x['latitude'] for x in c) / len(c)
                c_lon = sum(x['longitude'] for x in c) / len(c)
                if haversine(s['latitude'], s['longitude'], c_lat, c_lon) <= 400:
                    c.append(s)
                    placed = True
                    break
            if not placed:
                clusters.append([s])
                
        base_name = re.sub(r'\(.*?\)', '', group[0]['name']).strip()
        for c_idx, c in enumerate(clusters):
            c_hub = any(x['is_major_hub'] for x in c)
            c_lat = round(sum(x['latitude'] for x in c) / len(c), 6)
            c_lon = round(sum(x['longitude'] for x in c) / len(c), 6)
            c_name = base_name if len(clusters) == 1 else f"{base_name} ({c_idx + 1})"
            stage1.append({
                'name': c_name,
                'latitude': c_lat,
                'longitude': c_lon,
                'is_major_hub': c_hub,
                'corridor': c[0].get('corridor', 'Delhi Transit Region')
            })

print(f"Stage 1 stops count: {len(stage1)}")

# Stage 2: 75m spatial proximity merge
sorted_s1 = sorted(stage1, key=lambda s: (not s['is_major_hub'], s['name']))
final_stops = []
used = set()

for i, s1 in enumerate(sorted_s1):
    if i in used:
        continue
    cluster = [s1]
    used.add(i)
    for j in range(i + 1, len(sorted_s1)):
        if j in used:
            continue
        s2 = sorted_s1[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 75:  # Within 75m
            cluster.append(s2)
            used.add(j)
            
    is_hub = any(x['is_major_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_major_hub']]
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        clean_names = sorted([x['name'] for x in cluster], key=lambda x: ('(' in x, len(x), x))
        best_name = clean_names[0]
        best_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        best_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
        
    final_stops.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'is_major_hub': is_hub,
        'corridor': cluster[0]['corridor']
    })

print(f"Final Deduplicated Stops: {len(final_stops)}")
print(f"  Major Bus Stands (Black Dots): {sum(1 for s in final_stops if s['is_major_hub'])}")
print(f"  Regular Bus Stops (Blue Dots): {sum(1 for s in final_stops if not s['is_major_hub'])}")

# Check duplicate pairs within 70m
close = []
for i in range(len(final_stops)):
    s1 = final_stops[i]
    for j in range(i+1, len(final_stops)):
        s2 = final_stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 70:
            close.append((s1['name'], s2['name'], d))

print(f"\nRemaining pairs within 70m: {len(close)}")
for c in close:
    print(f"  {c[0]} <-> {c[1]} ({c[2]:.1f}m)")
