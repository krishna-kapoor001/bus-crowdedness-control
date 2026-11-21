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
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

# 1. Load Corridors
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

print(f"Loaded {len(auth_dict)} OSM Authoritative ground-truth stops.")

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
    # Strict Delhi NCT bounding box (0 outside Delhi!)
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
        unified_list.append({
            'name': orig_name.title() if orig_name.islower() else orig_name,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'is_major_hub': is_hub,
            'canonical_key': k
        })
        used_names.add(k)
    elif len(poles) == 1:
        lat, lon, _ = poles[0]
        unified_list.append({
            'name': disp,
            'latitude': round(lat, 6),
            'longitude': round(lon, 6),
            'is_major_hub': is_hub,
            'canonical_key': k
        })
        used_names.add(k)
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
            avg_lat = sum(p[0] for p in c) / len(c)
            avg_lon = sum(p[1] for p in c) / len(c)
            c_name = disp if len(clusters) == 1 else f"{disp} (Area {c_idx + 1})"
            unified_list.append({
                'name': c_name,
                'latitude': round(avg_lat, 6),
                'longitude': round(avg_lon, 6),
                'is_major_hub': is_hub,
                'canonical_key': clean_key(c_name)
            })
            used_names.add(clean_key(c_name))

# Ensure all 140+ authoritative ground-truth stops are included
for k, (orig_name, m_lat, m_lon, m_hub) in auth_dict.items():
    if k not in used_names:
        title_name = orig_name.title() if orig_name.islower() else orig_name
        unified_list.append({
            'name': title_name,
            'latitude': round(m_lat, 6),
            'longitude': round(m_lon, 6),
            'is_major_hub': m_hub,
            'canonical_key': k
        })
        used_names.add(k)

# SECONDARY SPATIAL PASS: Merge any two stops within 35 meters into exactly ONE physical stop!
# Hubs take priority so terminals and depots retain their proper name and black-dot status
sorted_stops = sorted(unified_list, key=lambda s: (not s['is_major_hub'], s['name']))
final_stops = []
merged_indices = set()

for i, s1 in enumerate(sorted_stops):
    if i in merged_indices:
        continue
    cluster = [s1]
    merged_indices.add(i)
    
    for j in range(i + 1, len(sorted_stops)):
        if j in merged_indices:
            continue
        s2 = sorted_stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 35:  # Within 35m across street or identical location
            cluster.append(s2)
            merged_indices.add(j)
            
    is_hub = any(c['is_major_hub'] for c in cluster)
    hub_stops = [c for c in cluster if c['is_major_hub']]
    
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        # Choose the cleanest, most concise name without parentheses
        clean_names = sorted([c['name'] for c in cluster], key=lambda x: ('(' in x, len(x), x))
        best_name = clean_names[0]
        best_lat = round(sum(c['latitude'] for c in cluster) / len(cluster), 6)
        best_lon = round(sum(c['longitude'] for c in cluster) / len(cluster), 6)
        
    final_stops.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'is_major_hub': is_hub,
        'merged_poles': len(cluster)
    })

print(f"\nFinal Deduplicated Single-Dot Stops: {len(final_stops)}")
major_hubs = [s for s in final_stops if s['is_major_hub']]
local_stops = [s for s in final_stops if not s['is_major_hub']]
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {len(major_hubs)}")
print(f"  Regular Bus Stops (Blue Dots): {len(local_stops)}")

# Check duplicate names and make 100% unique
name_freq = defaultdict(int)
for s in final_stops:
    name_freq[s['name']] += 1

uniquified_stops = []
seen_counts = defaultdict(int)
for s in final_stops:
    nm = s['name']
    if name_freq[nm] > 1:
        seen_counts[nm] += 1
        nm = f"{nm} ({seen_counts[nm]})"
    
    # Associate corridor & boardings
    lat, lon = s['latitude'], s['longitude']
    min_dist = float('inf')
    closest_corr = "Delhi Transit Region"
    for c in corridors:
        pts = c.get('coordinates', [])
        for pt in pts[::4]:
            d = math.hypot((lat - pt[0])*111000, (lon - pt[1])*111000)
            if d < min_dist:
                min_dist = d
                closest_corr = c.get('name', 'Delhi Transit Region').split('(')[0].strip()
    corridor = closest_corr if min_dist < 4000 else "Delhi Transit Region"
    boardings = 4200 if s['is_major_hub'] else max(400, int(1200 - min(800, min_dist * 0.2)))
    alightings = int(boardings * 0.95)
    
    uniquified_stops.append({
        'id': len(uniquified_stops) + 1,
        'name': nm,
        'latitude': lat,
        'longitude': lon,
        'corridor': corridor,
        'monthly_boardings': boardings,
        'monthly_alightings': alightings,
        'is_major_hub': s['is_major_hub']
    })

print(f"Total Unique Stops for Database: {len(uniquified_stops)}")

# 4. Save to JSON files
stop_profiles_path = os.path.join(PROCESSED_DIR, 'stop_profiles.json')
stops_meta_path = os.path.join(DATA_DIR, 'stops_meta.json')

clean_output = [
    {
        'name': s['name'],
        'latitude': s['latitude'],
        'longitude': s['longitude'],
        'corridor': s['corridor'],
        'monthly_boardings': s['monthly_boardings'],
        'monthly_alightings': s['monthly_alightings'],
        'is_major_hub': s['is_major_hub']
    }
    for s in uniquified_stops
]

with open(stop_profiles_path, 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

with open(stops_meta_path, 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

print(f"✓ Saved {len(clean_output)} stops to {stop_profiles_path}")
print(f"✓ Saved {len(clean_output)} stops to {stops_meta_path}")

# 5. Save to CSV files
csv_header = ['stop_id', 'stop_name', 'latitude', 'longitude', 'is_major_hub', 'corridor']
csv_rows = [
    [s['id'], s['name'], s['latitude'], s['longitude'], 1 if s['is_major_hub'] else 0, s['corridor']]
    for s in uniquified_stops
]

for csv_dest in [
    os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'),
    os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')
]:
    with open(csv_dest, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)
    print(f"✓ Saved {len(csv_rows)} rows to {csv_dest}")

# 6. Update SQLite flowpulse.db
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS stops_new")
c.execute("""
CREATE TABLE stops_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    corridor TEXT,
    monthly_boardings INTEGER,
    monthly_alightings INTEGER,
    is_major_hub BOOLEAN DEFAULT 0
)
""")

for s in uniquified_stops:
    c.execute("""
    INSERT INTO stops_new (name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (s['name'], s['latitude'], s['longitude'], s['corridor'], s['monthly_boardings'], s['monthly_alightings'], 1 if s['is_major_hub'] else 0))

c.execute("DROP TABLE IF EXISTS stops_old")
c.execute("ALTER TABLE stops RENAME TO stops_old")
c.execute("ALTER TABLE stops_new RENAME TO stops")
c.execute("DROP TABLE IF EXISTS stops_old")

c.execute("CREATE INDEX IF NOT EXISTS idx_stops_name ON stops(name)")
c.execute("CREATE INDEX IF NOT EXISTS idx_stops_coords ON stops(latitude, longitude)")
c.execute("CREATE INDEX IF NOT EXISTS idx_stops_is_major_hub ON stops(is_major_hub)")

conn.commit()
c.execute("SELECT count(*), sum(is_major_hub) FROM stops")
tot, hubs_cnt = c.fetchone()
conn.close()

print(f"✓ Successfully updated SQLite {DB_PATH}: {tot} total stops ({hubs_cnt} Major Bus Stands, {tot - hubs_cnt} Bus Stops).")
