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

def normalize_key(s):
    s = s.lower().strip()
    # remove terminal, stand, depot, isbt, etc. for root matching
    s = re.sub(r'\(.*?\)', ' ', s)
    s = re.sub(r'[^a-z0-9]', ' ', s)
    tokens = [w for w in s.split() if w not in ('terminal', 'depot', 'stand', 'isbt', 'crossing', 'xing', 'bus', 'stop')]
    return ' '.join(tokens)

# Load GROUND_TRUTH_STOPS from build_accurate_delhi_stops.py
import sys
sys.path.insert(0, '.')
from scripts.build_accurate_delhi_stops import GROUND_TRUTH_STOPS

# Build normalized GROUND_TRUTH_STOPS
gt_norm = {}
for k, v in GROUND_TRUTH_STOPS.items():
    k_clean = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]', ' ', k.lower())).strip()
    gt_norm[k_clean] = v
    k_root = normalize_key(k)
    if k_root and k_root not in gt_norm:
        gt_norm[k_root] = v

# Load GTFS stops
gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        try:
            name = row['stop_name']
            k_clean = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]', ' ', name.lower())).strip()
            k_root = normalize_key(name)
            gtfs_stops.append({
                'name': name,
                'clean': k_clean,
                'root': k_root,
                'lat': float(row['stop_lat']),
                'lon': float(row['stop_lon'])
            })
        except:
            pass

# Load current 429 stops
with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total current stops: {len(stops)}")
print(f"Total GTFS stops: {len(gtfs_stops)}")
print(f"Total GT Norm entries: {len(gt_norm)}")

# Test matching
matched_gt = 0
matched_gtfs_exact = 0
matched_gtfs_root = 0
fallback_count = 0

resolved = {}

for s in stops:
    name = s['name']
    cur_lat = s['latitude']
    cur_lon = s['longitude']
    k_clean = re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9]', ' ', name.lower())).strip()
    k_root = normalize_key(name)
    
    # Check 1: ground truth stops
    if k_clean in gt_norm:
        v = gt_norm[k_clean]
        resolved[name] = (v[0], v[1], 'ground_truth_clean')
        matched_gt += 1
        continue
    if k_root in gt_norm:
        v = gt_norm[k_root]
        resolved[name] = (v[0], v[1], 'ground_truth_root')
        matched_gt += 1
        continue
        
    # Check 2: exact clean in GTFS
    exact_gtfs = [g for g in gtfs_stops if g['clean'] == k_clean]
    if exact_gtfs:
        # Pick the one closest to current (or first)
        exact_gtfs.sort(key=lambda g: haversine(cur_lat, cur_lon, g['lat'], g['lon']))
        g = exact_gtfs[0]
        resolved[name] = (g['lat'], g['lon'], 'gtfs_exact')
        matched_gtfs_exact += 1
        continue
        
    # Check 3: root match in GTFS (if root length >= 4)
    if k_root and len(k_root) >= 4:
        root_gtfs = [g for g in gtfs_stops if g['root'] == k_root]
        if root_gtfs:
            root_gtfs.sort(key=lambda g: haversine(cur_lat, cur_lon, g['lat'], g['lon']))
            g = root_gtfs[0]
            # Verify not cross-city (> 15km)
            dist = haversine(cur_lat, cur_lon, g['lat'], g['lon'])
            if dist < 12.0:
                resolved[name] = (g['lat'], g['lon'], 'gtfs_root_close')
                matched_gtfs_root += 1
                continue

    # Fallback to current
    resolved[name] = (cur_lat, cur_lon, 'current_kept')
    fallback_count += 1

print(f"Matched GT: {matched_gt}")
print(f"Matched GTFS Exact: {matched_gtfs_exact}")
print(f"Matched GTFS Root: {matched_gtfs_root}")
print(f"Fallback Kept: {fallback_count}")

# Print fallbacks to inspect them
print("\n--- Fallbacks / Unmatched in direct passes ---")
for name, val in resolved.items():
    if val[2] == 'current_kept':
        print(f"  {name:<35} : ({val[0]}, {val[1]})")
