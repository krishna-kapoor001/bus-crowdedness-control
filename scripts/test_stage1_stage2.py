import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json, math, re
from collections import defaultdict

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Load authoritative OSM pins
from scripts.deploy_osm_tile_perfect_stops import OSM_TILE_PINS

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def base_canonical_name(s):
    # Remove (Area X), (Platform X), (N), (Temporary), etc.
    clean = re.sub(r'\(.*?\)', '', s).strip()
    clean = re.sub(r'[-_/]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def canonical_key(s):
    c = base_canonical_name(s).lower()
    return re.sub(r'[^a-z0-9]', '', c)

print(f"Initial stops count: {len(stops)}")

# Group stops by canonical key
groups = defaultdict(list)
for s in stops:
    k = canonical_key(s['name'])
    groups[k].append(s)

print(f"Unique canonical keys: {len(groups)}")

# Stage 1: Merge any stops sharing the same canonical key within 350 meters
stage1_stops = []
for k, group in groups.items():
    if len(group) == 1:
        s = group[0]
        s_clean_name = base_canonical_name(s['name'])
        stage1_stops.append({
            'name': s_clean_name,
            'latitude': s['latitude'],
            'longitude': s['longitude'],
            'is_major_hub': s['is_major_hub'],
            'corridor': s.get('corridor', 'Delhi Transit Region')
        })
    else:
        # Cluster within 350m
        clusters = []
        for s in group:
            placed = False
            for c in clusters:
                c_lat = sum(x['latitude'] for x in c) / len(c)
                c_lon = sum(x['longitude'] for x in c) / len(c)
                if haversine(s['latitude'], s['longitude'], c_lat, c_lon) <= 350:
                    c.append(s)
                    placed = True
                    break
            if not placed:
                clusters.append([s])
                
        base_name = base_canonical_name(group[0]['name'])
        for c_idx, c in enumerate(clusters):
            is_hub = any(x['is_major_hub'] for x in c)
            
            # Check if any in cluster matches OSM_TILE_PINS
            matched_pin = None
            for x in c:
                x_k = clean_key_str = re.sub(r'[^a-z0-9]', '', x['name'].lower())
                if x_k in OSM_TILE_PINS:
                    matched_pin = OSM_TILE_PINS[x_k]
                    break
            if not matched_pin and k in OSM_TILE_PINS:
                matched_pin = OSM_TILE_PINS[k]
                
            if matched_pin:
                chosen_lat, chosen_lon, is_h = matched_pin
                if is_h: is_hub = True
            else:
                chosen_lat = round(sum(x['latitude'] for x in c) / len(c), 6)
                chosen_lon = round(sum(x['longitude'] for x in c) / len(c), 6)
                
            # If there's only 1 cluster, use pure base_name (NO (Area 1)!)
            # If multiple distant clusters (>350m apart like different branches across Delhi), use area disambiguation
            c_name = base_name if len(clusters) == 1 else f"{base_name} ({c_idx + 1})"
            stage1_stops.append({
                'name': c_name,
                'latitude': chosen_lat,
                'longitude': chosen_lon,
                'is_major_hub': is_hub,
                'corridor': c[0].get('corridor', 'Delhi Transit Region')
            })

print(f"After Stage 1 (350m same-name merge): {len(stage1_stops)} stops")

# Stage 2: Spatial Proximity Merge (merge ANY two stops within 65m across Delhi)
# Terminals/Depots/Hubs take priority
sorted_s1 = sorted(stage1_stops, key=lambda s: (not s['is_major_hub'], s['name']))
stage2_stops = []
used_indices = set()

for i, s1 in enumerate(sorted_s1):
    if i in used_indices:
        continue
    cluster = [s1]
    used_indices.add(i)
    
    for j in range(i + 1, len(sorted_s1)):
        if j in used_indices:
            continue
        s2 = sorted_s1[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 65:  # Within 65 meters
            cluster.append(s2)
            used_indices.add(j)
            
    is_hub = any(x['is_major_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_major_hub']]
    
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        # Choose cleaner name
        clean_names = sorted([x['name'] for x in cluster], key=lambda x: ('(' in x, len(x), x))
        best_name = clean_names[0]
        best_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        best_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
        
    stage2_stops.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'is_major_hub': is_hub,
        'corridor': cluster[0]['corridor']
    })

print(f"After Stage 2 (65m spatial proximity merge): {len(stage2_stops)} stops")

# Check how many pairs are now within 60m
pairs_close = []
for i in range(len(stage2_stops)):
    s1 = stage2_stops[i]
    for j in range(i+1, len(stage2_stops)):
        s2 = stage2_stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 60:
            pairs_close.append((s1['name'], s2['name'], d))

print(f"Pairs within 60m: {len(pairs_close)}")

# Check Azad Market, Sarai Kale Khan, Vinod Nagar, Yamuna Vihar
print("\nSpot Checks:")
for test in ['azad market', 'sarai kale khan', 'east vinod nagar', 'yamuna vihar', 'akshardham', 'bentax', 'ip depot']:
    matches = [s for s in stage2_stops if test in s['name'].lower()]
    print(f"  Query '{test}' ({len(matches)} matches):")
    for m in matches:
        print(f"    • {m['name']}: [{m['latitude']}, {m['longitude']}] (Hub: {m['is_major_hub']})")
