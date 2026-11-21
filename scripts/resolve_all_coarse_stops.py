import json
import csv
import re
from math import radians, sin, cos, sqrt, atan2

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1 - a))

def clean_tokens(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    stopwords = {'terminal', 'depot', 'crossing', 'xing', 'stand', 'stop', 'station', 'isbt', 'chowk', 'cluster', 'road', 'marg', 'near', 'opp', 'gate', 'village', 'block', 'phase', 'sec', 'sector', 'more', 'mor', 't', 'bus'}
    return [t for t in s.split() if t not in stopwords and len(t) > 2]

# Load GTFS
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        name = row['stop_name']
        gtfs_stops.append({
            'name': name,
            'tokens': clean_tokens(name),
            'lat': float(row['stop_lat']),
            'lon': float(row['stop_lon'])
        })

# Load stops
with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Find all stops with coarse precision (<= 3 decimals in lat or lon)
coarse_stops = []
for s in stops:
    lat_str = str(s['latitude'])
    lon_str = str(s['longitude'])
    if len(lat_str.split('.')[-1]) <= 3 or len(lon_str.split('.')[-1]) <= 3:
        coarse_stops.append(s)

print(f"Total coarse stops to resolve: {len(coarse_stops)}")

resolved = {}
unresolved = []

for s in coarse_stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    s_tokens = clean_tokens(name)
    
    # Find matching GTFS stops within 3.0 km
    candidates = []
    for g in gtfs_stops:
        dist = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
        if dist < 3.0: # must be within 3 km of the locality
            common = set(s_tokens).intersection(set(g['tokens']))
            if common:
                score = len(common) / max(len(s_tokens), 1)
                candidates.append((score, dist, g))
                
    if candidates:
        # Sort by score desc, then dist asc
        candidates.sort(key=lambda x: (-x[0], x[1]))
        best = candidates[0]
        # Only accept if score >= 0.5 or high overlap
        if best[0] >= 0.4:
            resolved[name] = (best[2]['lat'], best[2]['lon'], best[2]['name'], round(best[1] * 1000, 1))
        else:
            unresolved.append((s, "Low score: " + str(best[0])))
    else:
        unresolved.append((s, "No candidate within 3km"))

print(f"Successfully matched to high-precision GTFS street coordinates: {len(resolved)} / {len(coarse_stops)}")
print(f"Unresolved: {len(unresolved)}")

print("\n--- SAMPLE RESOLUTIONS (Snapped from floating coords to exact street curb) ---")
for name, val in list(resolved.items())[:25]:
    print(f"'{name}' -> GTFS '{val[2]}' [{val[0]}, {val[1]}] (shifted {val[3]}m to road)")

if unresolved:
    print("\n--- UNRESOLVED STOPS ---")
    for u in unresolved:
        print(f"'{u[0]['name']}': ({u[0]['latitude']}, {u[0]['longitude']}) - {u[1]}")
