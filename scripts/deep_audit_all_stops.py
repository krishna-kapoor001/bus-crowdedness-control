import json
import csv
import re
from math import radians, sin, cos, sqrt, atan2

# 1. Load GTFS stops
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            gtfs_stops.append({
                'name': row['stop_name'],
                'lat': float(row['stop_lat']),
                'lon': float(row['stop_lon']),
            })
        except:
            pass

# 2. Load stop_profiles.json
with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    current_stops = json.load(f)

# Search functions
def find_candidates(name):
    # normalize tokens
    tokens = set(re.findall(r'[a-z0-9]+', name.lower()))
    tokens = {t for t in tokens if t not in {'terminal', 'depot', 'crossing', 'stand', 'stop', 'station', 'metro', 'isbt', 'chowk', 'cluster', 'road', 'marg'}}
    if not tokens:
        return []
    
    scored = []
    for g in gtfs_stops:
        g_tokens = set(re.findall(r'[a-z0-9]+', g['name'].lower()))
        common = tokens.intersection(g_tokens)
        if common:
            # score by fraction of query tokens found
            score = len(common) / len(tokens)
            if score >= 0.5:
                scored.append((score, g))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:5]

print(f"Total current stops: {len(current_stops)}")
unmatched = []
for s in current_stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    candidates = find_candidates(name)
    if not candidates:
        unmatched.append(s)

print(f"Completely unmatched stops in GTFS: {len(unmatched)}")
for u in unmatched:
    print(f"UNMATCHED: {u['name']} | ({u['latitude']}, {u['longitude']}) | Corridor: {u['corridor']}")
