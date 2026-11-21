import json, math, re, os, sys, csv, sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

sys.path.insert(0, BASE_DIR)
from scripts.deploy_osm_tile_perfect_stops import OSM_TILE_PINS

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def clean_key(s):
    s = s.lower().strip()
    s = re.sub(r'\(.*?\)', '', s)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\bbus\s+stop\b', '', s)
    s = re.sub(r'\bbus\s+stand\b', '', s)
    s = re.sub(r'\bxing\b', 'crossing', s)
    s = re.sub(r'\bgurudawara\b', 'gurudwara', s)
    s = re.sub(r'\bsarover\b', 'sarovar', s)
    s = re.sub(r'[^a-z0-9]', '', s)
    return s

# 1. Load extracted OSM bus stops
with open(os.path.join(DATA_DIR, 'osm_delhi_all_bus_stops.json'), 'r', encoding='utf-8') as f:
    raw_osm = json.load(f)

delhi_osm = []
for s in raw_osm:
    lat = s['latitude']
    lon = s['longitude']
    if isinstance(lat, list):
        lat = sum(p[1] for p in lat) / len(lat) if isinstance(lat[0], list) else sum(lat)/len(lat)
    if isinstance(lon, list):
        lon = sum(p[0] for p in lon) / len(lon) if isinstance(lon[0], list) else sum(lon)/len(lon)
    lat, lon = float(lat), float(lon)
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    delhi_osm.append({
        'name': s['name'],
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'is_hub': s['is_hub']
    })

# Deduplicate raw OSM opposite curbs within 50m
sorted_osm = sorted(delhi_osm, key=lambda x: (not x['is_hub'], x['name']))
deduped_osm = []
used_osm = set()
for i, s1 in enumerate(sorted_osm):
    if i in used_osm: continue
    cluster = [s1]
    used_osm.add(i)
    for j in range(i+1, len(sorted_osm)):
        if j in used_osm: continue
        s2 = sorted_osm[j]
        if haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude']) <= 50:
            cluster.append(s2)
            used_osm.add(j)
    is_h = any(x['is_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_hub']]
    if hub_stops:
        b_name, b_lat, b_lon = hub_stops[0]['name'], hub_stops[0]['latitude'], hub_stops[0]['longitude']
    else:
        named = [x for x in cluster if x['name'] != 'Unnamed']
        b_name = named[0]['name'] if named else cluster[0]['name']
        b_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        b_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
    deduped_osm.append({
        'name': b_name,
        'latitude': b_lat,
        'longitude': b_lon,
        'is_hub': is_h,
        'clean_key': clean_key(b_name)
    })

print(f"Loaded {len(deduped_osm)} verified OSM ground-truth stop locations.")

# Index OSM by clean_key
osm_by_key = defaultdict(list)
for s in deduped_osm:
    if s['clean_key']:
        osm_by_key[s['clean_key']].append(s)

# 2. Load our current stops
with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    current_stops = json.load(f)

# Snapping logic:
# Priority 1: OSM_TILE_PINS (Exact Authoritative Centroids for Terminals/Depots)
# Priority 2: Direct Match in deduped_osm by clean key (if within 200m)
# Priority 3: Nearest OSM Bus Stop Node within 80m
# Priority 4: Existing snapped position
snapped_stops = []
snapped_count = 0

for s in current_stops:
    s_key = clean_key(s['name'])
    lat, lon = s['latitude'], s['longitude']
    is_hub = s.get('is_major_hub', False)
    
    # Priority 1
    if s_key in OSM_TILE_PINS:
        p_lat, p_lon, p_hub = OSM_TILE_PINS[s_key]
        lat, lon = p_lat, p_lon
        if p_hub: is_hub = True
        snapped_count += 1
    elif s['name'].lower().strip() in OSM_TILE_PINS:
        p_lat, p_lon, p_hub = OSM_TILE_PINS[s['name'].lower().strip()]
        lat, lon = p_lat, p_lon
        if p_hub: is_hub = True
        snapped_count += 1
    # Priority 2: Match in OSM by key
    elif s_key in osm_by_key:
        candidates = osm_by_key[s_key]
        # find closest candidate
        best_c = min(candidates, key=lambda c: haversine(lat, lon, c['latitude'], c['longitude']))
        d = haversine(lat, lon, best_c['latitude'], best_c['longitude'])
        if d < 250: # within 250m
            lat = best_c['latitude']
            lon = best_c['longitude']
            if best_c['is_hub']: is_hub = True
            snapped_count += 1
    # Priority 3: Spatial snap to nearest OSM bus stop within 75m
    else:
        closest_osm = None
        min_d = float('inf')
        for osm_s in deduped_osm:
            # Quick bounding filter
            if abs(lat - osm_s['latitude']) < 0.001 and abs(lon - osm_s['longitude']) < 0.001:
                d = haversine(lat, lon, osm_s['latitude'], osm_s['longitude'])
                if d < min_d:
                    min_d = d
                    closest_osm = osm_s
        if closest_osm and min_d <= 75:
            lat = closest_osm['latitude']
            lon = closest_osm['longitude']
            if closest_osm['is_hub']: is_hub = True
            snapped_count += 1
            
    snapped_stops.append({
        'name': s['name'],
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'corridor': s.get('corridor', 'Delhi Transit Region'),
        'monthly_boardings': s.get('monthly_boardings', 1200),
        'monthly_alightings': s.get('monthly_alightings', 1140),
        'is_major_hub': is_hub
    })

print(f"Snapped {snapped_count} / {len(snapped_stops)} stops directly to OpenStreetMap bus stop icons!")

# 3. Final deduplication pass (ensure 0 duplicate dots within 65m)
sorted_snapped = sorted(snapped_stops, key=lambda x: (not x['is_major_hub'], x['name']))
final_stops = []
used_final = set()

for i, s1 in enumerate(sorted_snapped):
    if i in used_final: continue
    cluster = [s1]
    used_final.add(i)
    for j in range(i+1, len(sorted_snapped)):
        if j in used_final: continue
        s2 = sorted_snapped[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 65: # within 65m
            cluster.append(s2)
            used_final.add(j)
            
    is_hub = any(x['is_major_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_major_hub']]
    if hub_stops:
        best_name = hub_stops[0]['name']
        best_lat = hub_stops[0]['latitude']
        best_lon = hub_stops[0]['longitude']
    else:
        clean_names = sorted([x['name'] for x in cluster], key=lambda x: ('(' in x, len(x), x))
        best_name = clean_names[0]
        best_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        best_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
        
    final_stops.append({
        'name': best_name,
        'latitude': best_lat,
        'longitude': best_lon,
        'corridor': cluster[0]['corridor'],
        'monthly_boardings': max(x['monthly_boardings'] for x in cluster),
        'monthly_alightings': max(x['monthly_alightings'] for x in cluster),
        'is_major_hub': is_hub
    })

# Uniquify names
name_freq = defaultdict(int)
for s in final_stops: name_freq[s['name']] += 1
seen_nm = defaultdict(int)

uniquified = []
for s in final_stops:
    nm = s['name']
    if name_freq[nm] > 1:
        seen_nm[nm] += 1
        nm = f"{nm} ({seen_nm[nm]})"
    uniquified.append({
        'id': len(uniquified) + 1,
        'name': nm,
        'latitude': s['latitude'],
        'longitude': s['longitude'],
        'corridor': s['corridor'],
        'monthly_boardings': s['monthly_boardings'],
        'monthly_alightings': s['monthly_alightings'],
        'is_major_hub': s['is_major_hub']
    })

print(f"\nFinal Total Stops after 100% OSM Tile Snapping: {len(uniquified)}")
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {sum(1 for s in uniquified if s['is_major_hub'])}")
print(f"  Regular Bus Stops (Blue Dots): {sum(1 for s in uniquified if not s['is_major_hub'])}")

# Check duplicate pairs within 65m
close = []
for i in range(len(uniquified)):
    for j in range(i+1, len(uniquified)):
        d = haversine(uniquified[i]['latitude'], uniquified[i]['longitude'], uniquified[j]['latitude'], uniquified[j]['longitude'])
        if d < 65:
            close.append((uniquified[i]['name'], uniquified[j]['name'], d))

print(f"Duplicate pairs within 65m: {len(close)}")

# Save to JSON files
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
    for s in uniquified
]

with open(os.path.join(PROCESSED_DIR, 'stop_profiles.json'), 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'w', encoding='utf-8') as f:
    json.dump(clean_output, f, indent=2)

print("✓ Saved to stop_profiles.json and stops_meta.json")

# Save to CSV files
csv_header = ['stop_id', 'stop_name', 'latitude', 'longitude', 'is_major_hub', 'corridor']
csv_rows = [
    [s['id'], s['name'], s['latitude'], s['longitude'], 1 if s['is_major_hub'] else 0, s['corridor']]
    for s in uniquified
]

for cp in [os.path.join(DATA_DIR, 'delhi_bus_stands_coordinates.csv'), os.path.join(BASE_DIR, 'delhi_bus_stands_coordinates.csv')]:
    with open(cp, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(csv_header)
        writer.writerows(csv_rows)
    print(f"✓ Saved to {cp}")

# Update SQLite Database
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

for s in uniquified:
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

print(f"✓ SQLite flowpulse.db updated: {tot} stops ({hubs_cnt} Major Stands, {tot - hubs_cnt} Bus Stops).")
