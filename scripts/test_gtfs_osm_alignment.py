import json
import csv
import re
import math
from difflib import get_close_matches

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 # meters
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def normalize_name(s):
    if not s:
        return ""
    # remove brackets (1), (2), (up), (down), etc.
    s = re.sub(r'\s*\([0-9A-Za-z\s]+\)\s*', ' ', s)
    s = re.sub(r'\s*xing\b', ' Crossing', s, flags=re.IGNORECASE)
    s = re.sub(r'[^a-zA-Z0-9\s]', ' ', s)
    return ' '.join(s.lower().split())

# 1. Load official GTFS
gtfs_by_norm = {}
gtfs_all = []
with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        lat = float(row['stop_lat'])
        lon = float(row['stop_lon'])
        name = row['stop_name'].strip()
        item = {'name': name, 'lat': lat, 'lon': lon}
        gtfs_all.append(item)
        k = normalize_name(name)
        if k not in gtfs_by_norm:
            gtfs_by_norm[k] = []
        gtfs_by_norm[k].append(item)

# 2. Load OSM bus stops
osm_by_norm = {}
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)
    for o in osm_raw:
        name = (o.get('name') or '').strip()
        if not name or name.lower() == 'unnamed':
            continue
        lat = o.get('latitude')
        lon = o.get('longitude')
        # handle list format if any
        if isinstance(lat, list) and len(lat) == 2:
            lon, lat = lat[0], lat[1]
        elif isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
            pass
        else:
            continue
        item = {'name': name, 'lat': float(lat), 'lon': float(lon), 'is_hub': o.get('is_hub', False)}
        k = normalize_name(name)
        if k not in osm_by_norm:
            osm_by_norm[k] = []
        osm_by_norm[k].append(item)

print(f"Loaded {len(gtfs_all)} GTFS stops ({len(gtfs_by_norm)} unique normalized names)")
print(f"Loaded {len(osm_by_norm)} unique normalized OSM stop names")

# 3. Load current stop_profiles
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    current_stops = json.load(f)

print(f"Current stop_profiles stops: {len(current_stops)}")

# Ground Truth Delhi Transit Terminals / Hubs from OpenStreetMap & Delhi Govt Transport
MASTER_DELHI_HUBS = {
    "isbt kashmere gate": (28.6675, 77.2285),
    "kashmere gate": (28.6675, 77.2285),
    "anand vihar isbt": (28.6468, 77.3160),
    "anand vihar terminal": (28.6468, 77.3160),
    "isbt sarai kale khan": (28.5886, 77.2530),
    "sarai kale khan": (28.5886, 77.2530),
    "dhaula kuan": (28.5915, 77.1685),
    "aiims transit hub": (28.5685, 77.2115),
    "aiims": (28.5685, 77.2115),
    "nehru place terminal": (28.5485, 77.2520),
    "nehru place": (28.5485, 77.2520),
    "azadpur terminal": (28.7083, 77.1779),
    "azadpur": (28.7083, 77.1779),
    "shivaji stadium terminal": (28.6300, 77.2140),
    "shivaji stadium": (28.6300, 77.2140),
    "scindia house": (28.6304, 77.2177),
    "connaught place": (28.6304, 77.2177),
    "mehrauli terminal": (28.5195, 77.1818),
    "mehrauli": (28.5195, 77.1818),
    "badarpur border terminal": (28.4984, 77.3045),
    "badarpur border": (28.4984, 77.3045),
    "karol bagh terminal": (28.6500, 77.1900),
    "karol bagh": (28.6500, 77.1900),
    "uttam nagar terminal": (28.6250, 77.0655),
    "uttam nagar": (28.6250, 77.0655),
    "narela": (28.8520, 77.0940),
    "narela terminal": (28.8520, 77.0940),
    "mori gate terminal": (28.6650, 77.2250),
    "ambedkar stadium terminal": (28.6380, 77.2420),
    "anand parvat terminal": (28.6575, 77.1840),
    "kalyanpuri terminal": (28.6230, 77.3110),
    "mayur vihar phase 1": (28.6040, 77.2960),
    "mayur vihar phase 3 terminal": (28.6120, 77.3320),
    "rohini sector 22 terminal": (28.7250, 77.0680),
    "dwarka mor": (28.6190, 77.0330),
    "dwarka mor bus stand": (28.6190, 77.0330),
    "dwarka sector 10": (28.5810, 77.0570),
    "najafgarh terminal": (28.6150, 76.9770),
    "najafgarh": (28.6150, 76.9770),
    "shahdara terminal": (28.6740, 77.2870),
    "tilak nagar": (28.6360, 77.0960),
    "lajpat nagar": (28.5700, 77.2400),
    "iit gate": (28.5450, 77.1950),
    "munirka": (28.5580, 77.1740),
    "saket": (28.5204, 77.2100),
    "saket bus stop": (28.5204, 77.2100),
    "ito": (28.6290, 77.2490),
    "new delhi railway station": (28.6431, 77.2238),
    "old delhi railway station": (28.6565, 77.2305),
    "nizamuddin railway station": (28.5866, 77.2533)
}

# Test matching
matched_gtfs = 0
matched_osm = 0
matched_hubs = 0
unmatched_stops = []

for s in current_stops:
    name = s['name']
    norm = normalize_name(name)
    
    # 1. Check Master Hubs
    if norm in MASTER_DELHI_HUBS:
        matched_hubs += 1
        continue
    
    # 2. Check GTFS
    if norm in gtfs_by_norm:
        matched_gtfs += 1
        continue
    
    # 3. Check OSM
    if norm in osm_by_norm:
        matched_osm += 1
        continue
        
    unmatched_stops.append(name)

print(f"\nGround Truth Matching Results:")
print(f"  Master Delhi Hubs: {matched_hubs}")
print(f"  GTFS Direct Matches: {matched_gtfs}")
print(f"  OSM Direct Matches: {matched_osm}")
print(f"  Total Confirmed Ground Truth: {matched_hubs + matched_gtfs + matched_osm} / {len(current_stops)} ({((matched_hubs + matched_gtfs + matched_osm)/len(current_stops)*100):.1f}%)")
print(f"  Remaining to resolve: {len(unmatched_stops)}")
