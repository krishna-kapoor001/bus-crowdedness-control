import json
import math
import re

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

def get_tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', (name or '').lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'road', 'marg', 'delhi', 'village', 'cluster', 'depot', 'cws', 'ii', 'iv', 'metro', 'station', 'sec', 'sector', 'block'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

real_bus_stops = []
metro_track_coords = set()

for o in osm_raw:
    tags = o.get('tags', {})
    lat, lon = extract_coords(o)
    if not (lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6):
        continue
        
    if tags.get('operator') == 'Delhi Metro Rail Corporation Limited' and tags.get('highway') != 'bus_stop':
        metro_track_coords.add((round(lat, 5), round(lon, 5)))
        
    if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
        if tags.get('railway') == 'platform':
            continue
        name = (o.get('name') or tags.get('name') or '').strip()
        if not name or name.lower() in ['unnamed']:
            continue
        real_bus_stops.append({
            'name': name,
            'tokens': get_tokens(name),
            'lat': lat,
            'lon': lon,
            'tags': tags,
            'shelter': tags.get('shelter') == 'yes'
        })

print(f"Total authentic roadside bus stops in Delhi: {len(real_bus_stops)}")
print(f"Total DMRC train track nodes: {len(metro_track_coords)}")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

metro_stops_in_catalog = [
    s for s in catalog
    if (round(s['latitude'], 5), round(s['longitude'], 5)) in metro_track_coords
]

print(f"Catalog stops sitting on metro tracks / roadway centerlines: {len(metro_stops_in_catalog)}")

found_bus_stop = []
no_bus_stop = []

for s in metro_stops_in_catalog:
    s_toks = get_tokens(s['name'])
    best_b = None
    best_d = 999999
    
    for b in real_bus_stops:
        d = haversine(s['latitude'], s['longitude'], b['lat'], b['lon'])
        if d <= 350.0:
            overlap = s_toks & b['tokens']
            is_sub = (s['name'].lower() in b['name'].lower()) or (b['name'].lower() in s['name'].lower())
            if overlap or is_sub:
                bonus = 15 if b['shelter'] else 0
                eff_d = d - bonus
                if eff_d < best_d:
                    best_d = eff_d
                    best_b = (d, b)
                    
    if best_b:
        found_bus_stop.append((s, best_b[0], best_b[1]))
    else:
        no_bus_stop.append(s)

print(f"\n1. Metro track stops that CAN move onto real roadside bus stops: {len(found_bus_stop)}")
for s, d, b in found_bus_stop:
    print(f"  MOVE {d:.1f}m: '{s['name']}' -> Real Bus Stop '{b['name']}' at ({b['lat']}, {b['lon']}) [shelter={b['shelter']}]")

print(f"\n2. Metro track stops with NO bus stop nearby in OSM (true phantoms): {len(no_bus_stop)}")
for s in no_bus_stop:
    print(f"  PHANTOM: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - Hub: {s.get('is_major_hub')}")
