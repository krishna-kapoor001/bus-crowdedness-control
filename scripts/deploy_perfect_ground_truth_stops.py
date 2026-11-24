import json
import csv
import re
import math

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

def clean_display_name(name):
    # Strip (1), (2), etc. and standardize Crossing
    n = re.sub(r'\s*\([0-9A-Za-z\s]+\)\s*', ' ', name)
    n = re.sub(r'\s*xing\b', ' Crossing', n, flags=re.IGNORECASE)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

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

# 3. Master Delhi Hubs Ground Truth (Physical Terminals / Interchanges)
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
    "nizamuddin railway station": (28.5866, 77.2533),
    # Additional specific stops resolved
    "aero city": (28.5510, 77.1215),
    "alipur gt road": (28.8020, 77.1330),
    "badarpur m b road rajiv gandhi stadium": (28.4980, 77.3020),
    "barakhamba": (28.6300, 77.2270),
    "civil line": (28.6780, 77.2240),
    "dabri crossing dwarka road": (28.6080, 77.0860),
    "desu colony janakpuri": (28.6220, 77.0870),
    "devoli road crossing": (28.5080, 77.2340),
    "dwarka sec 21": (28.5520, 77.0580),
    "exchange store civil line": (28.6750, 77.2210),
    "g t k depot": (28.7180, 77.1850),
    "humayun road khan mkt": (28.6000, 77.2280),
    "ip depot bus stop": (28.6280, 77.2470),
    "ito agcr ito": (28.6290, 77.2430),
    "jln stadium terminal": (28.5870, 77.2370),
    "janakpuri district centre": (28.6290, 77.0780),
    "janakpuri east nangli zalib": (28.6280, 77.0880),
    "krishi bhawan rail bhawan": (28.6180, 77.2140),
    "madangir": (28.5220, 77.2310),
    "mahvir enclave part ii iii": (28.6040, 77.0760),
    "mukundpur chowk": (28.7350, 77.1840),
    "nhai building dwarka sec 10": (28.5840, 77.0570),
    "nand nagri depot": (28.6980, 77.3060),
    "narouji nagar": (28.5710, 77.1990),
    "p s nizamuddin": (28.5900, 77.2480),
    "p s pahar gunj": (28.6440, 77.2150),
    "qutub minar bus stopsation": (28.5240, 77.1860),
    "rohini depot 1": (28.7210, 77.0820),
    "rohini depot 2": (28.7280, 77.0700),
    "rohini sec 23 pkt 1": (28.7320, 77.0650),
    "seelam pur": (28.6670, 77.2680),
    "seelam pur bus stopmall": (28.6670, 77.2680),
    "shadipur dtc colony": (28.6510, 77.1580),
    "shakurpur jj colony britannia": (28.6870, 77.1520),
    "shastri park bus depot": (28.6730, 77.2560),
    "shastri park depot": (28.6730, 77.2560),
    "sheikh sarai phase ii shaheed bhagat singh college": (28.5360, 77.2180),
    "tagore garden tatarpur": (28.6440, 77.1130),
    "yamuna vihar ablock": (28.7010, 77.2720)
}

# 4. Load current stops
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    raw_stops = json.load(f)

# Step A: Group stops by clean base name to deduplicate (1) & (2) directional pairs
grouped = {}
for s in raw_stops:
    orig_name = s['name'].strip()
    clean_name = clean_display_name(orig_name)
    norm = normalize_name(clean_name)
    
    if norm not in grouped:
        grouped[norm] = []
    grouped[norm].append(s)

print(f"Grouped {len(raw_stops)} raw stops into {len(grouped)} unique canonical stop names")

deduped_stops = []
snapped_master_count = 0
snapped_gtfs_count = 0
snapped_osm_count = 0
fallback_count = 0

for norm_key, stop_list in grouped.items():
    # Pick the representative stop
    rep = stop_list[0]
    display_name = clean_display_name(rep['name'])
    
    # Merge monthly boardings and alightings across duplicate pairs
    total_boardings = sum(s.get('monthly_boardings', 0) for s in stop_list)
    total_alightings = sum(s.get('monthly_alightings', 0) for s in stop_list)
    is_hub = any(s.get('is_major_hub', False) for s in stop_list)
    corridor = rep.get('corridor', 'Delhi Transit Corridor')
    
    # Coordinate resolution priority:
    # Priority 1: Master Delhi Transit Hubs / Terminals Ground Truth
    if norm_key in MASTER_DELHI_HUBS:
        lat, lon = MASTER_DELHI_HUBS[norm_key]
        snapped_master_count += 1
    # Priority 2: Official Delhi Transport Department GTFS GPS Survey
    elif norm_key in gtfs_by_norm:
        candidates = gtfs_by_norm[norm_key]
        lat, lon = candidates[0]['lat'], candidates[0]['lon']
        snapped_gtfs_count += 1
    # Priority 3: OpenStreetMap Bus Stops
    elif norm_key in osm_by_norm:
        candidates = osm_by_norm[norm_key]
        lat, lon = candidates[0]['lat'], candidates[0]['lon']
        snapped_osm_count += 1
    # Priority 4: Existing coordinate (already high quality)
    else:
        lat, lon = rep['latitude'], rep['longitude']
        fallback_count += 1
        
    deduped_stops.append({
        'name': display_name,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'corridor': corridor,
        'monthly_boardings': total_boardings,
        'monthly_alightings': total_alightings,
        'is_major_hub': is_hub
    })

# Sort by monthly boardings descending
deduped_stops.sort(key=lambda x: x['monthly_boardings'], reverse=True)

print(f"\nFinal Deduplication & Snapping Summary:")
print(f"  Total canonical stops: {len(deduped_stops)}")
print(f"  Snapped to Master Hubs: {snapped_master_count}")
print(f"  Snapped to Official GTFS: {snapped_gtfs_count}")
print(f"  Snapped to Real OSM: {snapped_osm_count}")
print(f"  Retained coordinates: {fallback_count}")

# Check duplicate locations (< 35m) in the final dataset
close_pairs = []
for i in range(len(deduped_stops)):
    for j in range(i + 1, len(deduped_stops)):
        d = haversine(
            deduped_stops[i]['latitude'], deduped_stops[i]['longitude'],
            deduped_stops[j]['latitude'], deduped_stops[j]['longitude']
        )
        if d < 35:
            close_pairs.append((deduped_stops[i]['name'], deduped_stops[j]['name'], d))

print(f"\nStops within 35m in final dataset: {len(close_pairs)}")
for cp in close_pairs[:10]:
    print(f"  {cp[0]} <---> {cp[1]} ({cp[2]:.1f}m)")
