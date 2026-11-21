import json, math, re, os, sys, csv, sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')

sys.path.insert(0, BASE_DIR)
from scripts.perfect_bus_stands_dedup import AUTHORITATIVE_HUBS

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def clean_stop_name(name):
    s = name.strip()
    s = re.sub(r'\(.*?\)', '', s).strip()
    s = re.sub(r'\bbus\s+stop\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bbus\s+stand\b', '', s, flags=re.IGNORECASE)
    s = re.sub(r'\bxing\b', 'crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'\bgurudawara\b', 'gurudwara', s, flags=re.IGNORECASE)
    s = re.sub(r'\bsarover\b', 'sarovar', s, flags=re.IGNORECASE)
    s = re.sub(r'[-_/]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def canonical_key(s):
    c = clean_stop_name(s).lower()
    return re.sub(r'[^a-z0-9]', '', c)

# 1. Load pure OSM bus stops
with open(os.path.join(DATA_DIR, 'osm_delhi_all_bus_stops.json'), 'r', encoding='utf-8') as f:
    raw_osm = json.load(f)

pure_osm = []
for s in raw_osm:
    tags = s.get('tags', {})
    hway = tags.get('highway')
    amen = tags.get('amenity')
    pub = tags.get('public_transport')
    op = tags.get('operator', '').lower()
    
    # Exclude metro, railway, tracks
    if 'metro' in op or 'railway' in op or 'indian railways' in op or pub == 'stop_position':
        continue
    if hway != 'bus_stop' and amen != 'bus_station' and pub != 'platform':
        continue
        
    lat = s['latitude']
    lon = s['longitude']
    if isinstance(lat, list) or isinstance(lon, list): continue
    lat, lon = float(lat), float(lon)
    
    # Strictly Delhi NCT
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
    # Exclude Haryana/UP regions
    name_low = s['name'].lower()
    if any(out in name_low or out in op for out in ['noida', 'gurugram', 'gmcbl', 'ghaziabad', 'faridabad', 'upsrtc']):
        continue
        
    clean_n = clean_stop_name(s['name'])
    if not clean_n or clean_n.lower() in ['unnamed', 'stop']:
        continue
        
    pure_osm.append({
        'name': clean_n,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'is_hub': s['is_hub'] or any(t in clean_n.lower() for t in ['terminal', 'depot', 'isbt'])
    })

print(f"Total Pure Delhi OSM Stops loaded: {len(pure_osm)}")

# Deduplicate OSM stops: merge opposite curbs within 65m
sorted_osm = sorted(pure_osm, key=lambda x: (not x['is_hub'], x['name']))
osm_deduped = []
used_osm = set()

for i, s1 in enumerate(sorted_osm):
    if i in used_osm: continue
    cluster = [s1]
    used_osm.add(i)
    for j in range(i+1, len(sorted_osm)):
        if j in used_osm: continue
        s2 = sorted_osm[j]
        if haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude']) <= 65:
            cluster.append(s2)
            used_osm.add(j)
            
    is_hub = any(x['is_hub'] for x in cluster)
    hub_stops = [x for x in cluster if x['is_hub']]
    if hub_stops:
        b_name, b_lat, b_lon = hub_stops[0]['name'], hub_stops[0]['latitude'], hub_stops[0]['longitude']
    else:
        # Pick cleanest name
        b_name = sorted(cluster, key=lambda x: len(x['name']))[0]['name']
        b_lat = round(sum(x['latitude'] for x in cluster) / len(cluster), 6)
        b_lon = round(sum(x['longitude'] for x in cluster) / len(cluster), 6)
        
    osm_deduped.append({
        'name': b_name,
        'latitude': b_lat,
        'longitude': b_lon,
        'is_hub': is_hub,
        'clean_key': canonical_key(b_name)
    })

print(f"Unified OSM Stops (0 duplicates within 65m): {len(osm_deduped)}")

# Check duplicate pairs in osm_deduped
pairs_close = 0
for i in range(len(osm_deduped)):
    for j in range(i+1, len(osm_deduped)):
        if haversine(osm_deduped[i]['latitude'], osm_deduped[i]['longitude'], osm_deduped[j]['latitude'], osm_deduped[j]['longitude']) < 65:
            pairs_close += 1
print(f"OSM Pairs within 65m: {pairs_close}")

# Inspect Yamuna Vihar, Shahdara, Kashmere Gate
for q in ['yamuna vihar', 'shahdara', 'kashmere gate', 'anand vihar']:
    m = [s for s in osm_deduped if q in s['name'].lower()]
    print(f"\nMatches for '{q}': {len(m)}")
    for x in m:
        print(f"  • {x['name']}: [{x['latitude']}, {x['longitude']}] (Hub: {x['is_hub']})")
