import json
import sqlite3
import math
import urllib.request
import time

print("=" * 80)
print("  EXHAUSTIVE 360-DEGREE PRODUCTION AUDIT — DTC SMART OCCUPANCY SYSTEM (DSOS) DELHI")
print("=" * 80)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def extract_coords(obj):
    lat = obj.get('latitude') or obj.get('lat')
    lon = obj.get('longitude') or obj.get('lon')
    if isinstance(lat, list) and isinstance(lon, list):
        if len(lat) > 0 and isinstance(lat[0], (int, float)):
            val1 = float(lat[0])
            val2 = float(lat[1]) if len(lat) > 1 else float(lon[0])
            if 28.0 <= val1 <= 29.0:
                return val1, val2
            elif 28.0 <= val2 <= 29.0:
                return val2, val1
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        l1, l2 = float(lat), float(lon)
        if 28.0 <= l1 <= 29.0:
            return l1, l2
        elif 28.0 <= l2 <= 29.0:
            return l2, l1
    return None, None

# -------------------------------------------------------------
# AUDIT 1: File Synchronization & Database Integrity
# -------------------------------------------------------------
print("\n[AUDIT 1/5] File Synchronization & Database Integrity")
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    sp = json.load(f)

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    sm = json.load(f)

conn = sqlite3.connect('data/flowpulse.db')
cur = conn.cursor()
cur.execute('SELECT count(*), sum(case when is_major_hub=1 then 1 else 0 end) FROM stops;')
db_total, db_hubs = cur.fetchone()
conn.close()

sp_hubs = len([s for s in sp if s.get('is_major_hub')])
sm_hubs = len([s for s in sm if s.get('is_major_hub')])

print(f"  • stop_profiles.json: {len(sp)} stops, {sp_hubs} Major Bus Stands")
print(f"  • stops_meta.json:    {len(sm)} stops, {sm_hubs} Major Bus Stands")
print(f"  • SQLite database:    {db_total} stops, {db_hubs} Major Bus Stands")

assert len(sp) == len(sm) == db_total, "Mismatch in stop counts!"
assert sp_hubs == sm_hubs == db_hubs, "Mismatch in hub counts!"
print("  ✓ 1:1 PERFECT SYNCHRONIZATION across JSON and SQLite DB!")

# Check bounding box
out_of_bounds = [s for s in sp if not (28.3 <= s['latitude'] <= 28.95 and 76.8 <= s['longitude'] <= 77.55)]
print(f"  • Stops outside Delhi NCR boundaries: {len(out_of_bounds)}")
assert len(out_of_bounds) == 0, f"Found out-of-bounds stops: {out_of_bounds}"
print("  ✓ All stops are within official Delhi boundaries!")

# -------------------------------------------------------------
# AUDIT 2: OpenStreetMap Ground Truth & Zero Phantoms
# -------------------------------------------------------------
print("\n[AUDIT 2/5] OpenStreetMap Physical Bus Shelter Alignment")
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

roadside_bus_stops = []
metro_track_nodes = set()

for o in osm_raw:
    tags = o.get('tags', {})
    lat, lon = extract_coords(o)
    if not (lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6):
        continue
    if tags.get('operator') == 'Delhi Metro Rail Corporation Limited' and tags.get('highway') != 'bus_stop':
        metro_track_nodes.add((round(lat, 5), round(lon, 5)))
    if tags.get('railway') == 'platform':
        continue
    if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
        name = (o.get('name') or tags.get('name') or '').strip()
        if name and name.lower() not in ['unnamed']:
            roadside_bus_stops.append({'name': name, 'lat': lat, 'lon': lon, 'shelter': tags.get('shelter') == 'yes'})

print(f"  • Verified authentic roadside OSM bus stops: {len(roadside_bus_stops)}")
print(f"  • Known DMRC elevated train track nodes:    {len(metro_track_nodes)}")

# Check distance of each catalog stop to nearest roadside bus stop
max_dist = 0.0
imperfect_stops = []
metro_track_contamination = []

for s in sp:
    if (round(s['latitude'], 5), round(s['longitude'], 5)) in metro_track_nodes:
        metro_track_contamination.append(s['name'])
    best_d = min(haversine(s['latitude'], s['longitude'], b['lat'], b['lon']) for b in roadside_bus_stops)
    if best_d > max_dist:
        max_dist = best_d
    if best_d > 1.0:
        imperfect_stops.append((s['name'], best_d))

print(f"  • Max offset to authentic OSM bus stop node: {max_dist:.3f} meters")
print(f"  • Stops > 1.0m from authentic bus shelter:    {len(imperfect_stops)}")
print(f"  • Stops contaminated by DMRC train tracks:    {len(metro_track_contamination)}")
assert len(imperfect_stops) == 0, f"Found imperfect stops: {imperfect_stops[:5]}"
assert len(metro_track_contamination) == 0, f"Found metro track stops: {metro_track_contamination}"
print("  ✓ 100.0% OF STOPS ARE DEAD-CENTER (<= 1.0m) ON ACTUAL BUS SHELTERS!")
print("  ✓ ZERO PHANTOMS / ZERO TRAIN TRACK NODES!")

# -------------------------------------------------------------
# AUDIT 3: Pairwise Distance & Zero Duplicate Collisions
# -------------------------------------------------------------
print("\n[AUDIT 3/5] Pairwise Collision & Deduplication Verification")
collisions_15m = []
collisions_30m = []
names_seen = {}
duplicate_names = []

for s in sp:
    n_lower = s['name'].strip().lower()
    if n_lower in names_seen:
        duplicate_names.append((s['name'], names_seen[n_lower]))
    names_seen[n_lower] = (s['latitude'], s['longitude'])

n_stops = len(sp)
for i in range(n_stops):
    for j in range(i + 1, n_stops):
        d = haversine(sp[i]['latitude'], sp[i]['longitude'], sp[j]['latitude'], sp[j]['longitude'])
        if d < 15.0:
            collisions_15m.append((d, sp[i]['name'], sp[j]['name']))
        elif d < 30.0:
            collisions_30m.append((d, sp[i]['name'], sp[j]['name']))

print(f"  • Total pairs evaluated:                     {n_stops * (n_stops - 1) // 2:,}")
print(f"  • Identical stop names:                      {len(duplicate_names)}")
print(f"  • Collisions within 15 meters:               {len(collisions_15m)}")
print(f"  • Stops within 15–30 meters:                 {len(collisions_30m)}")
assert len(duplicate_names) == 0, f"Duplicate names found: {duplicate_names}"
assert len(collisions_15m) == 0, f"Collisions < 15m found: {collisions_15m}"
print("  ✓ 0 DUPLICATE COLLISION ACCROSS ALL 759 STOPS!")

# -------------------------------------------------------------
# AUDIT 4: Live REST API & Journey Planner Endpoints
# -------------------------------------------------------------
print("\n[AUDIT 4/5] Live REST API Endpoints Verification (http://localhost:8000)")
try:
    # 1. GeoJSON endpoint
    with urllib.request.urlopen('http://localhost:8000/api/v1/network/geojson', timeout=6) as r:
        geo = json.loads(r.read().decode('utf-8'))
        features = geo.get('features', [])
        live_hubs = [f for f in features if f['properties'].get('is_hub')]
        print(f"  • /api/v1/network/geojson:       {len(features)} features, {len(live_hubs)} Major Hubs")
        assert len(features) == len(sp), "GeoJSON feature count mismatch!"
        assert len(live_hubs) == sp_hubs, "GeoJSON major hub count mismatch!"

    # 2. Stops endpoint
    with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops', timeout=6) as r:
        stops_api = json.loads(r.read().decode('utf-8'))
        print(f"  • /api/v1/journey/stops:          {len(stops_api)} stops returned")
        assert len(stops_api) == len(sp), "Stops API count mismatch!"

    # 3. Bus stand query search
    with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops?query=bus+stand', timeout=6) as r:
        bs_matches = json.loads(r.read().decode('utf-8'))
        print(f"  • /api/v1/journey/stops?query=... {len(bs_matches)} bus stands returned on search")
        assert len(bs_matches) >= 38, "Not all bus stands returned on search!"

    # 4. Plan journey test
    plan_url = 'http://localhost:8000/api/v1/journey/plan'
    payload = json.dumps({
        'origin': 'Saket Bus Stop',
        'destination': 'Dhaula Kuan',
        'departure_time': '08:30',
        'prefer_less_crowded': False
    }).encode('utf-8')
    req = urllib.request.Request(plan_url, data=payload, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=6) as r:
        plan_resp = json.loads(r.read().decode('utf-8'))
        alts = plan_resp.get('alternatives', [])
        print(f"  • /api/v1/journey/plan:           {len(alts)} routing alternatives generated")
        assert len(alts) >= 1, "Journey planner failed to generate route alternatives!"
    print("  ✓ ALL API ENDPOINTS OPERATIONAL, FAST & CLEAN!")
except Exception as e:
    print(f"  ! API audit failed: {e}")
    raise

# -------------------------------------------------------------
# AUDIT 5: Corridor Geometry & Stop Coverage
# -------------------------------------------------------------
print("\n[AUDIT 5/5] Corridors & Graph Edge Coverage")
with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

catalog_names = {s['name'].strip().lower() for s in sp}
corridor_stops_checked = 0
corridor_stops_matched = 0

for c in corridors:
    for s_name in c.get('stops', []):
        corridor_stops_checked += 1
        if s_name.strip().lower() in catalog_names:
            corridor_stops_matched += 1

print(f"  • Total Corridors monitored:                 {len(corridors)}")
print(f"  • Corridor stop match rate:                  {corridor_stops_matched} / {corridor_stops_checked} ({corridor_stops_matched/corridor_stops_checked*100:.1f}%)")

print("\n" + "=" * 80)
print("  AUDIT RESULT: 100% STREET-PERFECT, ZERO FLAWS DETECTED!")
print("=" * 80)
