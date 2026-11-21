import csv
import json
import math
import os
import re
import sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

# 1. Load corridors
with open(os.path.join(PROCESSED_DIR, 'corridors_routed.json'), 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# 2. Extract OSM_AUTHORITATIVE
auth_dict = {}
with open(os.path.join(BASE_DIR, 'scripts', 'perfect_street_snapping_all_428.py'), 'r', encoding='utf-8') as f:
    code = f.read()
    match = re.search(r'OSM_AUTHORITATIVE\s*=\s*\{([^}]+)\}', code, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            m = re.match(r"['\"]([^'\"]+)['\"]\s*:\s*\(([^,]+),\s*([^,]+),\s*(True|False)\)", line)
            if m:
                clean_k = re.sub(r'[^a-z0-9]', '', m.group(1).lower())
                auth_dict[clean_k] = (m.group(1), float(m.group(2)), float(m.group(3)), m.group(4) == 'True')

# 3. Load GTFS stops
with open(os.path.join(DATA_DIR, 'gtfs_delhi_stops.txt'), 'r', encoding='utf-8') as f:
    gtfs_rows = list(csv.DictReader(f))

def normalize_name(s):
    s = s.strip()
    s = re.sub(r'Metro\s*(?:Station|Stn)?', ' Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Bus Stop\)', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'Bus Stop\s+Bus Stop', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def clean_key(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Group poles by canonical key
groups = defaultdict(list)
display_map = {}
for r in gtfs_rows:
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])
    # Strict Delhi NCT bounding box
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    norm = normalize_name(r['stop_name'])
    k = clean_key(norm)
    groups[k].append((lat, lon, norm))
    if k not in display_map:
        display_map[k] = norm

unified_list = []
used_names = set()

for k, poles in groups.items():
    disp = display_map[k]
    is_hub = any(t in k for t in ['terminal', 'depot', 'isbt', 'busstand'])
    
    # Check if authoritative ground truth exists
    if k in auth_dict:
        orig_name, lat, lon, is_h = auth_dict[k]
        if is_h: is_hub = True
        chosen_lat, chosen_lon = lat, lon
        unified_list.append({
            'name': disp,
            'latitude': round(chosen_lat, 6),
            'longitude': round(chosen_lon, 6),
            'is_major_hub': is_hub
        })
        used_names.add(disp.lower())
    elif len(poles) == 1:
        lat, lon, _ = poles[0]
        unified_list.append({
            'name': disp,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'is_major_hub': is_hub
        })
        used_names.add(disp.lower())
    else:
        # Multiple poles across the street:
        # Spatial clustering (radius 150m) to merge opposite-side curbs into 1 physical stop
        clusters = []
        for p_lat, p_lon, p_name in poles:
            placed = False
            for c in clusters:
                c_lat = sum(p[0] for p in c) / len(c)
                c_lon = sum(p[1] for p in c) / len(c)
                if haversine(p_lat, p_lon, c_lat, c_lon) <= 150:
                    c.append((p_lat, p_lon, p_name))
                    placed = True
                    break
            if not placed:
                clusters.append([(p_lat, p_lon, p_name)])
        
        for c_idx, c in enumerate(clusters):
            # Centroid of opposite curbs
            avg_lat = sum(p[0] for p in c) / len(c)
            avg_lon = sum(p[1] for p in c) / len(c)
            
            c_name = disp if len(clusters) == 1 else f"{disp} (Area {c_idx + 1})"
            unified_list.append({
                'name': c_name,
                'latitude': round(avg_lat, 6),
                'longitude': round(avg_lon, 6),
                'is_major_hub': is_hub
            })
            used_names.add(c_name.lower())

# Ensure all 144 authoritative hubs/stops are present (e.g. DTC Bus Depot Yamuna Vihar)
for k, (orig_name, m_lat, m_lon, m_hub) in auth_dict.items():
    if orig_name.lower() not in used_names:
        unified_list.append({
            'name': orig_name,
            'latitude': round(m_lat, 6),
            'longitude': round(m_lon, 6),
            'is_major_hub': m_hub
        })
        used_names.add(orig_name.lower())

print(f"Total Unified Delhi Stops: {len(unified_list)}")
hubs = [s for s in unified_list if s['is_major_hub']]
stops = [s for s in unified_list if not s['is_major_hub']]
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {len(hubs)}")
print(f"  Regular Bus Stops (Blue Dots): {len(stops)}")

# Check duplicate names
all_names = [s['name'] for s in unified_list]
print(f"Unique names: {len(set(all_names))} / Total: {len(all_names)}")

# Check close proximity (< 25m)
pairs_close = 0
for i in range(len(unified_list)):
    s1 = unified_list[i]
    for j in range(i+1, len(unified_list)):
        s2 = unified_list[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 25:
            pairs_close += 1
print(f"Stops within 25m of each other: {pairs_close}")
