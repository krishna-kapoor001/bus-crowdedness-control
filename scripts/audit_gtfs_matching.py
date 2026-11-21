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

def clean_str(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    return ' '.join(s.split())

# 1. Load GTFS stops
gtfs_by_clean = {}
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            name = row['stop_name']
            c = clean_str(name)
            lat = float(row['stop_lat'])
            lon = float(row['stop_lon'])
            item = {'name': name, 'clean': c, 'lat': lat, 'lon': lon, 'code': row['stop_code']}
            gtfs_stops.append(item)
            if c not in gtfs_by_clean:
                gtfs_by_clean[c] = []
            gtfs_by_clean[c].append(item)
        except:
            pass

# 2. Load current stops
with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    current_stops = json.load(f)

# 3. Check exact clean match in GTFS for each stop
perfect_matches = []
multiple_matches = []
unmatched = []

for s in current_stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    c = clean_str(name)
    
    if c in gtfs_by_clean:
        candidates = gtfs_by_clean[c]
        if len(candidates) == 1:
            g = candidates[0]
            dist = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            perfect_matches.append((s, g, dist))
        else:
            # Sort by distance to current
            candidates.sort(key=lambda g: haversine(cur_lat, cur_lon, g['lat'], g['lon']))
            g = candidates[0]
            dist = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            multiple_matches.append((s, g, dist, len(candidates)))
    else:
        unmatched.append(s)

print(f"Total current stops: {len(current_stops)}")
print(f"Single exact clean match in GTFS: {len(perfect_matches)}")
print(f"Multiple exact clean match in GTFS: {len(multiple_matches)}")
print(f"Unmatched in clean match: {len(unmatched)}")

# Let's inspect where dist > 1km in perfect_matches
print("\n--- Perfect Name Match but Distance > 1km ---")
for s, g, dist in sorted(perfect_matches, key=lambda x: x[2], reverse=True):
    if dist > 1.0:
        print(f"'{s['name']}' | Cur: ({s['latitude']}, {s['longitude']}) -> GTFS: '{g['name']}' ({g['lat']}, {g['lon']}) | Dist: {round(dist, 2)} km")

# Let's inspect where dist > 1km in multiple_matches
print("\n--- Multiple Matches but Distance > 1km ---")
for s, g, dist, count in sorted(multiple_matches, key=lambda x: x[2], reverse=True):
    if dist > 1.0:
        print(f"'{s['name']}' ({count} cand) | Cur: ({s['latitude']}, {s['longitude']}) -> Best GTFS: '{g['name']}' ({g['lat']}, {g['lon']}) | Dist: {round(dist, 2)} km")
