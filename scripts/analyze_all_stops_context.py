import json
import csv
import re
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# 1. Load GTFS stops
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            gtfs_stops.append({
                'id': row['stop_id'],
                'code': row['stop_code'],
                'name': row['stop_name'],
                'lat': float(row['stop_lat']),
                'lon': float(row['stop_lon']),
            })
        except:
            pass

# 2. Load stop_profiles.json
with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    current_stops = json.load(f)

# 3. Load corridors_routed.json
corridor_stops_map = {}
with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corridors = json.load(f)
    for c in corridors:
        stops_in_c = c.get('stops', [])
        for idx, s in enumerate(stops_in_c):
            if s not in corridor_stops_map:
                corridor_stops_map[s] = []
            corridor_stops_map[s].append((c['name'], idx, c.get('coordinates', [])))

print(f"Loaded {len(gtfs_stops)} GTFS stops, {len(current_stops)} stops, {len(corridors)} corridors.")

# Clean token set
def clean_tokens(text):
    text = text.lower()
    text = re.sub(r'\(.*?\)', ' ', text)
    text = re.sub(r'[^a-z0-9]', ' ', text)
    stopwords = {'terminal', 'depot', 'crossing', 'stand', 'stop', 'station', 'metro', 'isbt', 'chowk', 'cluster', 'road', 'marg', 'near', 'opp', 'gate', 'village', 'block', 'phase', 'sec', 'sector', 'more', 'mor'}
    return [t for t in text.split() if t not in stopwords and len(t) > 2]

# Build index of GTFS stops
gtfs_token_map = {}
for g in gtfs_stops:
    tokens = clean_tokens(g['name'])
    for t in tokens:
        if t not in gtfs_token_map:
            gtfs_token_map[t] = []
        gtfs_token_map[t].append(g)

results = []
for s in current_stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    tokens = clean_tokens(name)
    
    # Corridor context
    corr_info = corridor_stops_map.get(name, [])
    
    # Candidate GTFS stops
    candidate_scores = {}
    for t in tokens:
        for g in gtfs_token_map.get(t, []):
            gid = g['code'] + '_' + g['name']
            if gid not in candidate_scores:
                candidate_scores[gid] = {'stop': g, 'matches': 0}
            candidate_scores[gid]['matches'] += 1
            
    # Filter candidates having highest matches
    if candidate_scores:
        candidates = list(candidate_scores.values())
        max_matches = max(c['matches'] for c in candidates)
        best_candidates = [c['stop'] for c in candidates if c['matches'] == max_matches]
        
        # If there are corridor coordinates, find candidate closest to corridor trajectory
        # Otherwise find candidate closest to current coordinates
        dists = []
        for g in best_candidates:
            d = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            dists.append((d, g))
        dists.sort(key=lambda x: x[0])
        best_dist, best_g = dists[0]
        results.append({
            'name': name,
            'cur': (cur_lat, cur_lon),
            'gtfs': best_g,
            'dist_km': best_dist,
            'is_hub': s.get('is_major_hub', False)
        })
    else:
        results.append({
            'name': name,
            'cur': (cur_lat, cur_lon),
            'gtfs': None,
            'dist_km': 0,
            'is_hub': s.get('is_major_hub', False)
        })

# Analyze distances
over_1km = [r for r in results if r['dist_km'] > 1.0]
over_300m = [r for r in results if 0.3 < r['dist_km'] <= 1.0]
under_300m = [r for r in results if r['gtfs'] and r['dist_km'] <= 0.3]
no_match = [r for r in results if not r['gtfs']]

print(f"\nAudit Summary:")
print(f"Under 300m (Accurate): {len(under_300m)}")
print(f"300m - 1km (Slightly displaced): {len(over_300m)}")
print(f"Over 1km (Significantly misplaced): {len(over_1km)}")
print(f"No token match in GTFS: {len(no_match)}")

print("\n--- STOPS OVER 1KM AWAY ---")
for r in sorted(over_1km, key=lambda x: x['dist_km'], reverse=True):
    print(f"{r['name']:<35} | Cur: {r['cur']} | GTFS: {r['gtfs']['name']:<30} {r['gtfs']['lat'], r['gtfs']['lon']} | Dist: {round(r['dist_km'], 2)} km | Hub: {r['is_hub']}")
