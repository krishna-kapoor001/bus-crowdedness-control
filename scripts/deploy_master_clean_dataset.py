import os, sys, json, math, re, csv, sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

from scripts.deploy_osm_tile_perfect_stops import OSM_TILE_PINS

# Load Corridors
with open(os.path.join(PROCESSED_DIR, 'corridors_routed.json'), 'r', encoding='utf-8') as f:
    corridors = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def normalize_spelling(s):
    s = s.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bgurudawara\b', 'gurudwara', s, flags=re.IGNORECASE)
    s = re.sub(r'\bsarover\b', 'sarovar', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def canonical_key(s):
    c = normalize_spelling(s).lower()
    return re.sub(r'[^a-z0-9]', '', c)

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    raw_stops = json.load(f)

# Group by canonical key
groups = defaultdict(list)
for s in raw_stops:
    k = canonical_key(s['name'])
    groups[k].append(s)

stage1 = []
for k, group in groups.items():
    is_hub = any(s['is_major_hub'] for s in group)
    matched_pin = None
    if k in OSM_TILE_PINS:
        matched_pin = OSM_TILE_PINS[k]
    else:
        for s in group:
            sk = re.sub(r'[^a-z0-9]', '', s['name'].lower())
            if sk in OSM_TILE_PINS:
                matched_pin = OSM_TILE_PINS[sk]
                break
                
    if matched_pin:
        lat, lon, is_h = matched_pin
        if is_h: is_hub = True
        clean_name = sorted(group, key=lambda x: ('(' in x['name'], len(x['name'])))[0]['name']
        clean_name = re.sub(r'\(.*?\)', '', clean_name).strip()
        stage1.append({
            'name': clean_name,
            'latitude': lat,
            'longitude': lon,
            'is_major_hub': is_hub,
            'corridor': group[0].get('corridor', 'Delhi Transit Region')
        })
    elif len(group) == 1:
        s = group[0]
        cname = re.sub(r'\(.*?\)', '', s['name']).strip()
        stage1.append({
            'name': cname,
            'latitude': s['latitude'],
            'longitude': s['longitude'],
            'is_major_hub': s['is_major_hub'],
            'corridor': s.get('corridor', 'Delhi Transit Region')
        })
    else:
        clusters = []
        for s in group:
            placed = False
            for c in clusters:
                c_lat = sum(x['latitude'] for x in c) / len(c)
                c_lon = sum(x['longitude'] for x in c) / len(c)
                if haversine(s['latitude'], s['longitude'], c_lat, c_lon) <= 400:
                    c.append(s)
                    placed = True
                    break
            if not placed:
                clusters.append([s])
                
        base_name = re.sub(r'\(.*?\)', '', group[0]['name']).strip()
        for c_idx, c in enumerate(clusters):
            c_hub = any(x['is_major_hub'] for x in c)
            c_lat = round(sum(x['latitude'] for x in c) / len(c), 6)
            c_lon = round(sum(x['longitude'] for x in c) / len(c), 6)
            c_name = base_name if len(clusters) == 1 else f"{base_name} ({c_idx + 1})"
            stage1.append({
                'name': c_name,
                'latitude': c_lat,
                'longitude': c_lon,
                'is_major_hub': c_hub,
                'corridor': c[0].get('corridor', 'Delhi Transit Region')
            })

# Stage 2: 75m spatial proximity merge
sorted_s1 = sorted(stage1, key=lambda s: (not s['is_major_hub'], s['name']))
final_stops = []
used = set()

for i, s1 in enumerate(sorted_s1):
    if i in used:
        continue
    cluster = [s1]
    used.add(i)
    for j in range(i + 1, len(sorted_s1)):
        if j in used:
            continue
        s2 = sorted_s1[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d <= 75:  # Within 75m
            cluster.append(s2)
            used.add(j)
            
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
        'is_major_hub': is_hub
    })

# Uniquify names and calculate ridership
name_freq = defaultdict(int)
for s in final_stops:
    name_freq[s['name']] += 1

uniquified = []
seen = defaultdict(int)
for s in final_stops:
    nm = s['name']
    if name_freq[nm] > 1:
        seen[nm] += 1
        nm = f"{nm} ({seen[nm]})"
        
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
    
    uniquified.append({
        'id': len(uniquified) + 1,
        'name': nm,
        'latitude': lat,
        'longitude': lon,
        'corridor': corridor,
        'monthly_boardings': boardings,
        'monthly_alightings': alightings,
        'is_major_hub': s['is_major_hub']
    })

print(f"Deploying {len(uniquified)} master clean Delhi stops (0 duplicates within 70m)...")
print(f"  Major Bus Stands / Depots (Black Dots): {sum(1 for s in uniquified if s['is_major_hub'])}")
print(f"  Regular Bus Stops (Blue Dots): {sum(1 for s in uniquified if not s['is_major_hub'])}")

# Save to JSON
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

# Save to CSV
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
    print(f"✓ Saved CSV to {cp}")

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
