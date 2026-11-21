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
    s = s.lower()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    stopwords = {'terminal', 'depot', 'crossing', 'stand', 'stop', 'station', 'metro', 'isbt', 'chowk', 'cluster', 'road', 'marg', 'near', 'opp', 'gate', 'village', 'block', 'phase', 'sec', 'sector', 'more', 'mor', 't'}
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

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    current_stops = json.load(f)

print(f"Inspecting {len(current_stops)} stops:")
matched_count = 0
misplaced_candidates = []

for s in current_stops:
    s_tokens = clean_tokens(s['name'])
    cur_lat, cur_lon = s['latitude'], s['longitude']
    
    candidates = []
    for g in gtfs_stops:
        common = set(s_tokens).intersection(set(g['tokens']))
        if common:
            score = len(common) / max(len(s_tokens), 1)
            dist = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            candidates.append((score, dist, g))
            
    # Check if matched by high score
    high_score = [c for c in candidates if c[0] >= 0.7]
    if high_score:
        high_score.sort(key=lambda x: (-x[0], x[1]))
        best = high_score[0]
        if best[1] > 2.0:
            misplaced_candidates.append((s, best[2], best[1], best[0]))

print(f"\nTotal potential misplaced stops with strong token match (>2km offset): {len(misplaced_candidates)}")
for s, g, dist, score in misplaced_candidates:
    print(f"MISPLACED: '{s['name']}' ({s['latitude']}, {s['longitude']}) -> GTFS: '{g['name']}' ({g['lat']}, {g['lon']}) | Dist: {round(dist, 2)}km | Corridor: {s['corridor']}")
