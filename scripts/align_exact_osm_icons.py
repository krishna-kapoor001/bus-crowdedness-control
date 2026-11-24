import json
import math
import re

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def parse_coord(val):
    if isinstance(val, (list, tuple)):
        return float(val[0])
    return float(val)

def normalize(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def get_tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', name.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'road', 'marg', 'delhi', 'village'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

# Step 1: Load current stops
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Initial stops count: {len(stops)}")

# Step 2: Merge deep clusters
merge_map = {
    'Rani Jhansi Road Jhande Walan': 'Jhandewalan',
    'Nehru Place Apartments': 'Nehru Place Crossing Paras Cinema',
    'Maya Puri Crossing Ring Road': 'Mayapuri Depot',
    'B3 Keshav Puram': 'B 4 Keshav Puram',
    'C 8 Keshav Puram': 'B 4 Keshav Puram',
    'Raghubir Nagar F Block': 'Khayala More Subhash Nagar Crossing',
}

extra_b = {}
extra_a = {}
for s in stops:
    if s['name'] in merge_map:
        target = merge_map[s['name']]
        extra_b[target] = extra_b.get(target, 0) + s.get('monthly_boardings', 0)
        extra_a[target] = extra_a.get(target, 0) + s.get('monthly_alightings', 0)

filtered = []
for s in stops:
    if s['name'] in merge_map:
        continue
    if s['name'] in extra_b:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + extra_b[s['name']]
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + extra_a[s['name']]
    filtered.append(s)

print(f"Stops count after deep cluster merges: {len(filtered)}")

# Step 3: Load OSM stops
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

# Build list of valid OSM nodes
osm_nodes = []
for o in osm_raw:
    name = (o.get('name') or '').strip()
    lat = parse_coord(o.get('latitude') or o.get('lat'))
    lon = parse_coord(o.get('longitude') or o.get('lon'))
    if not (28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6):
        continue
    tags = o.get('tags', {})
    
    # Score how likely this node is the one rendered on tiles with icon & text:
    # 1. highway=bus_stop with shelter or operator or explicit platform is the visible tile icon
    score = 0
    if tags.get('highway') == 'bus_stop':
        score += 10
    if tags.get('public_transport') == 'platform':
        score += 5
    if tags.get('shelter') == 'yes':
        score += 3
    if tags.get('operator'):
        score += 2
    if tags.get('public_transport') == 'stop_position':
        score -= 5  # de-prioritize in-roadway stop_position
    if tags.get('operator') == 'Delhi Metro Rail Corporation Limited' and 'metro' not in name.lower():
        score -= 3  # metro train platforms labeled as stop_position
        
    osm_nodes.append({
        'name': name,
        'norm': normalize(name),
        'tokens': get_tokens(name),
        'lat': lat,
        'lon': lon,
        'tags': tags,
        'score': score
    })

print(f"Loaded {len(osm_nodes)} candidate OSM nodes in Delhi bbox.")

# Specific fix for Hansraj College:
# Node 4 (28.6792029, 77.2081931) is the exact tile icon node with shelter and DTIDC operator!
for s in filtered:
    if s['name'] == 'Hansraj College':
        s['latitude'] = 28.679203
        s['longitude'] = 77.208193
        print("Explicitly aligned Hansraj College to exact OSM tile icon: (28.679203, 77.208193)")

# Step 4: For every stop, find if an alternate OSM node with exact name match has higher visual score
improved_snaps = 0
for s in filtered:
    if s['name'] == 'Hansraj College':
        continue
    s_norm = normalize(s['name'])
    s_toks = get_tokens(s['name'])
    
    # Find all OSM nodes within 65m
    local_candidates = []
    for o in osm_nodes:
        # Match if exact normalized name OR significant token overlap
        is_name_match = (o['norm'] == s_norm)
        if not is_name_match and s_toks and o['tokens']:
            if s_toks == o['tokens'] or (len(s_toks & o['tokens']) >= max(len(s_toks), len(o['tokens'])) - 1 and len(s_toks & o['tokens']) >= 2):
                is_name_match = True
                
        if is_name_match:
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d <= 65.0:
                local_candidates.append((d, o['score'], o))
                
    if local_candidates:
        # Sort by visual score descending, then distance ascending
        local_candidates.sort(key=lambda x: (-x[1], x[0]))
        best_d, best_score, best_o = local_candidates[0]
        # If best_score > 5 and distance is between 3m and 60m, align to it!
        if best_score >= 10 and best_d > 4.0:
            s['latitude'] = round(best_o['lat'], 6)
            s['longitude'] = round(best_o['lon'], 6)
            improved_snaps += 1

print(f"Refined {improved_snaps} stops directly onto highest-scoring visible OSM tile icon nodes!")

# Step 5: Save updated datasets
filtered.sort(key=lambda x: x['monthly_boardings'], reverse=True)

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print(f"Successfully saved {len(filtered)} verified stops to stop_profiles.json and stops_meta.json!")
