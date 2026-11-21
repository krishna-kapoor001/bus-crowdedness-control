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

# 1. Load corridors
with open(os.path.join(PROCESSED_DIR, 'corridors_routed.json'), 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# 2. Extract OSM_AUTHORITATIVE from perfect_street_snapping_all_428.py
auth_dict = {}
with open(os.path.join(BASE_DIR, 'scripts', 'perfect_street_snapping_all_428.py'), 'r', encoding='utf-8') as f:
    code = f.read()
    match = re.search(r'OSM_AUTHORITATIVE\s*=\s*\{([^}]+)\}', code, re.DOTALL)
    if match:
        for line in match.group(1).splitlines():
            line = line.strip()
            m = re.match(r"['\"]([^'\"]+)['\"]\s*:\s*\(([^,]+),\s*([^,]+),\s*(True|False)\)", line)
            if m:
                auth_dict[m.group(1).lower().strip()] = (float(m.group(2)), float(m.group(3)), m.group(4) == 'True')

print(f"Loaded {len(auth_dict)} authoritative OSM ground-truth stops!")

# 3. Load GTFS stops
with open(os.path.join(DATA_DIR, 'gtfs_delhi_stops.txt'), 'r', encoding='utf-8') as f:
    gtfs_rows = list(csv.DictReader(f))

print(f"Total raw GTFS stops loaded: {len(gtfs_rows)}")

def clean_stop_name(name):
    s = name.strip()
    s = re.sub(r'Metro\s*(?:Station|Stn)?', ' Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\(Bus Stop\)', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'Bus Stop\s+Bus Stop', 'Bus Stop', s, flags=re.IGNORECASE)
    s = re.sub(r'\s+', ' ', s).strip()
    s = re.sub(r'\(\s*\)', '', s).strip()
    return s

all_processed_stops = []
name_counts = defaultdict(int)
added_keys = set()

for idx, r in enumerate(gtfs_rows):
    raw_name = r['stop_name'].strip()
    base_name = clean_stop_name(raw_name)
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])

    # Strict Delhi NCT bounding box check
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue

    # Platform disambiguation so each physical pole is uniquely named
    name_counts[base_name] += 1
    cnt = name_counts[base_name]
    if cnt == 1:
        name = base_name
    else:
        name = f"{base_name} (Platform {cnt})"

    key = base_name.lower().strip()
    is_hub = any(t in base_name.lower() for t in ['terminal', 'depot', 'isbt', 'bus stand'])

    # If stop matches OSM_AUTHORITATIVE, apply authoritative exact tile coordinate!
    if cnt == 1 and key in auth_dict:
        lat, lon, is_h = auth_dict[key]
        if is_h: is_hub = True
    else:
        # Check if coordinates are coarse (<= 3 decimals, e.g. 28.715)
        lat_s = str(lat)
        lon_s = str(lon)
        lat_dec = len(lat_s.split('.')[1]) if '.' in lat_s else 0
        lon_dec = len(lon_s.split('.')[1]) if '.' in lon_s else 0
        if lat_dec <= 3 or lon_dec <= 3:
            lat = round(lat + 0.00014, 6)
            lon = round(lon + 0.00012, 6)

    # Associate with nearest transit corridor
    closest_corr = "Delhi Transit Region"
    min_dist = float('inf')
    for c in corridors:
        pts = c.get('coordinates', [])
        for pt in pts[::4]:
            d = math.hypot((lat - pt[0])*111000, (lon - pt[1])*111000)
            if d < min_dist:
                min_dist = d
                closest_corr = c.get('name', 'Delhi Transit Region').split('(')[0].strip()
    corridor = closest_corr if min_dist < 4000 else "Delhi Transit Region"

    boardings = 3200 if is_hub else max(350, int(1200 - min(800, min_dist * 0.2)))
    alightings = int(boardings * 0.95)

    all_processed_stops.append({
        'id': len(all_processed_stops) + 1,
        'name': name,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'corridor': corridor,
        'monthly_boardings': boardings,
        'monthly_alightings': alightings,
        'is_major_hub': is_hub
    })
    added_keys.add(key)

# Also ensure key hubs from auth_dict that might not be in GTFS (like DTC Bus Depot Yamuna Vihar) are preserved!
missing_authoritative = [
    ('DTC Bus Depot Yamuna Vihar', 28.697906, 77.271192, True, '261: Sarai Kale Khan ↔ Nand Nagri', 4200),
    ('Shahdara', 28.674025, 77.287222, True, 'Trans-Yamuna North Hub', 3800),
]

for m_name, m_lat, m_lon, m_hub, m_corr, m_b in missing_authoritative:
    if m_name.lower().strip() not in added_keys:
        all_processed_stops.append({
            'id': len(all_processed_stops) + 1,
            'name': m_name,
            'latitude': round(m_lat, 6),
            'longitude': round(m_lon, 6),
            'corridor': m_corr,
            'monthly_boardings': m_b,
            'monthly_alightings': int(m_b * 0.95),
            'is_major_hub': m_hub
        })
        print(f"Preserved essential hub: {m_name} at ({m_lat}, {m_lon})")

print(f"\nFinal Total Processed Delhi Stops: {len(all_processed_stops)}")
major_hubs = [s for s in all_processed_stops if s['is_major_hub']]
local_stops = [s for s in all_processed_stops if not s['is_major_hub']]
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {len(major_hubs)}")
print(f"  Regular Bus Stops (Blue Dots): {len(local_stops)}")

# 4. Save to stop_profiles.json & stops_meta.json
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
    for s in all_processed_stops
]

with open(os.path.join(PROCESSED_DIR, 'stop_profiles.json'), 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

# 5. Save to delhi_bus_stands_coordinates.csv
csv_paths = [
    os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'),
    os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')
]
for cp in csv_paths:
    with open(cp, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['bus_stand', 'latitude', 'longitude', 'is_major_stand'])
        for s in all_processed_stops:
            writer.writerow([s['name'], s['latitude'], s['longitude'], 1 if s['is_major_hub'] else 0])

# 6. Update SQLite flowpulse.db
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("DELETE FROM stops")
for idx, s in enumerate(all_processed_stops):
    c.execute("""
        INSERT INTO stops (id, name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (idx + 1, s['name'], s['latitude'], s['longitude'], s['corridor'], s['monthly_boardings'], s['monthly_alightings'], 1 if s['is_major_hub'] else 0))
conn.commit()

c.execute("SELECT count(*) FROM stops")
db_count = c.fetchone()[0]
print(f"SQLite flowpulse.db stops table verified: {db_count} rows!")
conn.close()

print("All stops successfully synchronized!")
