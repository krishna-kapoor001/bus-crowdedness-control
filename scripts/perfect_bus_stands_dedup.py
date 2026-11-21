import json, sqlite3, math, re, os, sys, csv
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

# Load all stops from flowpulse.db
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute('SELECT id, name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub FROM stops')
all_stops = [
    {
        'id': r[0],
        'name': r[1],
        'latitude': r[2],
        'longitude': r[3],
        'corridor': r[4],
        'monthly_boardings': r[5],
        'monthly_alightings': r[6],
        'is_major_hub': bool(r[7])
    }
    for r in c.fetchall()
]
conn.close()

# Authoritative centroids for major bus stands / terminals / ISBTs / depots
AUTHORITATIVE_HUBS = {
    'isbt kashmere gate': (28.668690, 77.230420, 'ISBT Kashmere Gate'),
    'anand vihar isbt': (28.646753, 77.318004, 'Anand Vihar ISBT'),
    'sarai kale khan isbt': (28.585038, 77.258760, 'Sarai Kale Khan ISBT'),
    'dtc bus depot yamuna vihar': (28.697906, 77.271192, 'DTC Bus Depot Yamuna Vihar'),
    'shahdara terminal': (28.674078, 77.287596, 'Shahdara Terminal'),
    'mori gate terminal': (28.668361, 77.225176, 'Mori Gate Terminal'),
    'nehru place terminal': (28.548100, 77.255200, 'Nehru Place Terminal'),
    'mehrauli terminal': (28.522469, 77.182353, 'Mehrauli Terminal'),
    'najafgarh terminal': (28.612500, 76.986500, 'Najafgarh Terminal'),
    'uttam nagar terminal': (28.626125, 77.068310, 'Uttam Nagar Terminal'),
    'karampura terminal': (28.660349, 77.143945, 'Karampura Terminal'),
    'punjabi bagh terminal': (28.667300, 77.137322, 'Punjabi Bagh Terminal'),
    'badarpur border terminal': (28.493283, 77.303366, 'Badarpur Border Terminal'),
    'ambedkar nagar terminal': (28.514075, 77.228304, 'Ambedkar Nagar Terminal'),
    'kendriya terminal': (28.623500, 77.204500, 'Kendriya Terminal'),
    'shivaji stadium terminal': (28.632517, 77.215525, 'Shivaji Stadium Terminal'),
    'nand nagri depot': (28.697809, 77.305701, 'Nand Nagri Depot'),
    'wazirpur depot': (28.693572, 77.155382, 'Wazirpur Depot'),
    'hasanpur depot': (28.635019, 77.307667, 'Hasanpur Depot'),
    'kalkaji depot': (28.538073, 77.267806, 'Kalkaji Depot'),
    'bawana depot': (28.795523, 77.042137, 'Bawana Depot'),
    'peera garhi depot': (28.678000, 77.093000, 'Peera Garhi Depot'),
    'vasant vihar depot': (28.558000, 77.158000, 'Vasant Vihar Depot'),
    'mayapuri depot': (28.630588, 77.129781, 'Mayapuri Depot'),
    'shadipur depot': (28.653193, 77.156028, 'Shadipur Depot'),
    'east vinod nagar depot': (28.620715, 77.300806, 'East Vinod Nagar Depot'),
    'dhaula kuan': (28.590797, 77.168346, 'Dhaula Kuan'),
    'aiims': (28.568983, 77.213433, 'AIIMS Transit Hub'),
    'azadpur terminal': (28.708330, 77.177920, 'Azadpur Terminal'),
    'new delhi railway station': (28.642000, 77.221000, 'New Delhi Railway Station'),
    'old delhi railway station': (28.657000, 77.228000, 'Old Delhi Railway Station'),
    'nizamuddin railway station': (28.588000, 77.251000, 'Nizamuddin Railway Station'),
    'rajghat depot': (28.643957, 77.252596, 'Rajghat Cluster Depot'),
    'shastri park depot': (28.674092, 77.243445, 'Shastri Park Depot'),
    'qamruddin nagar terminal': (28.682102, 77.054233, 'Qamruddin Nagar Terminal'),
    'jln stadium terminal': (28.591124, 77.233243, 'JLN Stadium Terminal'),
    'rohini depot 1': (28.716427, 77.113439, 'Rohini Depot 1'),
    'rohini depot 2': (28.729875, 77.121641, 'Rohini Depot 2'),
    'rohini depot 3': (28.695489, 77.109000, 'Rohini Depot 3'),
    'sarojini nagar depot': (28.573454, 77.189987, 'Sarojini Nagar Depot'),
    'naraina depot': (28.648745, 77.151268, 'Naraina Depot'),
    'hari nagar depot': (28.624629, 77.101942, 'Hari Nagar Depot'),
    'dichau kalan depot': (28.629331, 76.997946, 'Dichau Kalan Depot'),
    'gazipur depot': (28.641887, 77.315806, 'Gazipur Depot'),
    'tehkhand depot': (28.510934, 77.281042, 'Tehkhand Depot DTC'),
    'sukhdev vihar depot': (28.554487, 77.271482, 'Sukhdev Vihar Depot'),
    'kair depot': (28.618203, 76.930728, 'Kair Depot'),
    'kalyan puri terminal': (28.616875, 77.317853, 'Kalyan Puri Terminal'),
    'kalyan vihar terminal': (28.693476, 77.199021, 'Kalyan Vihar Terminal'),
    'karol bagh terminal': (28.648029, 77.200844, 'Karol Bagh Terminal'),
    'anand parvat terminal': (28.657498, 77.183984, 'Anand Parvat Terminal'),
    'malka ganj terminal': (28.677501, 77.207823, 'Malka Ganj Terminal'),
    'mangla puri terminal': (28.589839, 77.086416, 'Mangla Puri Terminal'),
    'pragati maidan terminal': (28.612700, 77.245000, 'Pragati Maidan Terminal'),
    'raja garden terminal': (28.654629, 77.123382, 'Raja Garden Terminal'),
    'sultanpuri terminal': (28.703250, 77.075267, 'Sultanpuri Terminal'),
    'vivek vihar terminal': (28.668228, 77.314389, 'Vivek Vihar Terminal'),
    'west enclave terminal': (28.691667, 77.100991, 'West Enclave Terminal'),
}

# For each authoritative hub:
# Find all stops within 400m of its coordinate that are hubs or duplicate representations
# Merge them into EXACTLY 1 Black Dot at the authoritative coordinate!
# Any other road stop within the cluster that is clearly a curbside stop becomes a regular blue dot or is merged.
processed_stops = []
claimed_stop_ids = set()

for hk, (h_lat, h_lon, h_display) in AUTHORITATIVE_HUBS.items():
    # Find all stops near this hub
    near = [s for s in all_stops if haversine(s['latitude'], s['longitude'], h_lat, h_lon) <= 450]
    # Match candidates by name or hub flag
    hub_candidates = [
        s for s in near 
        if s['is_major_hub'] or any(t in s['name'].lower() for t in ['terminal', 'depot', 'isbt', 'bus stand'])
    ]
    if not hub_candidates and near:
        # Closest stop
        hub_candidates = [min(near, key=lambda s: haversine(s['latitude'], s['longitude'], h_lat, h_lon))]
        
    if hub_candidates:
        # Combine boardings
        tot_b = max(4200, sum(s['monthly_boardings'] for s in hub_candidates))
        corr = hub_candidates[0]['corridor']
        for s in hub_candidates:
            claimed_stop_ids.add(s['id'])
    else:
        tot_b = 4500
        corr = 'Delhi Transit Region'
        
    processed_stops.append({
        'name': h_display,
        'latitude': round(h_lat, 6),
        'longitude': round(h_lon, 6),
        'corridor': corr,
        'monthly_boardings': tot_b,
        'monthly_alightings': int(tot_b * 0.95),
        'is_major_hub': True
    })

print(f"Locked {len(processed_stops)} authoritative major bus stands/depots/terminals (1 per facility)!")

# Add remaining stops that were not merged into authoritative hubs
remaining_stops = [s for s in all_stops if s['id'] not in claimed_stop_ids]
for s in remaining_stops:
    # If it was marked hub but not in AUTHORITATIVE_HUBS, check if it's within 60m of an authoritative hub
    too_close_to_hub = any(haversine(s['latitude'], s['longitude'], h['latitude'], h['longitude']) <= 60 for h in processed_stops)
    if too_close_to_hub:
        continue
    # Non-authoritative hubs that are genuine standalone regional terminals (like Rohini Sec 22 Terminal, Jheel Terminal, etc.)
    # keep them, otherwise keep as regular stop
    is_h = s['is_major_hub']
    # Filter artificial hubs
    if any(t in s['name'].lower() for t in ['train depot', 'cargo express', 'airforce', 'noval', 'supply depot']):
        is_h = False
        
    processed_stops.append({
        'name': s['name'],
        'latitude': s['latitude'],
        'longitude': s['longitude'],
        'corridor': s['corridor'],
        'monthly_boardings': s['monthly_boardings'],
        'monthly_alightings': s['monthly_alightings'],
        'is_major_hub': is_h
    })

# Uniquify names and final 60m proximity check
name_freq = defaultdict(int)
for s in processed_stops: name_freq[s['name']] += 1
seen = defaultdict(int)

final_clean = []
for s in processed_stops:
    nm = s['name']
    if name_freq[nm] > 1:
        seen[nm] += 1
        nm = f"{nm} ({seen[nm]})"
    final_clean.append({
        'id': len(final_clean) + 1,
        'name': nm,
        'latitude': s['latitude'],
        'longitude': s['longitude'],
        'corridor': s['corridor'],
        'monthly_boardings': s['monthly_boardings'],
        'monthly_alightings': s['monthly_alightings'],
        'is_major_hub': s['is_major_hub']
    })

print(f"\nFinal Verified Stops: {len(final_clean)}")
hubs_cnt = sum(1 for s in final_clean if s['is_major_hub'])
stops_cnt = sum(1 for s in final_clean if not s['is_major_hub'])
print(f"  Major Bus Stands / Terminals / Depots (Black Dots): {hubs_cnt}")
print(f"  Regular Bus Stops (Blue Dots): {stops_cnt}")

# Check Kashmere Gate, Anand Vihar, Yamuna Vihar, Wazirpur specifically
print("\nSpot Checks on Bus Stands:")
for q in ['kashmere gate', 'anand vihar', 'yamuna vihar', 'wazirpur', 'hasanpur', 'kalkaji', 'shahdara']:
    matches = [s for s in final_clean if q in s['name'].lower() and s['is_major_hub']]
    print(f"  Query '{q}' ({len(matches)} Major Stand Black Dots):")
    for m in matches:
        print(f"    • {m['name']}: [{m['latitude']}, {m['longitude']}]")

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
    for s in final_clean
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
    for s in final_clean
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

for s in final_clean:
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
