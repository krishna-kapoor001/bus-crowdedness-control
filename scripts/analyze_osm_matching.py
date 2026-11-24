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

def clean_name(n):
    n = n.lower()
    for drop in ['terminal', 'depot', 'bus stop', 'bus stand', 'crossing', 'more', 'mor', 'isbt', 'dtc']:
        n = re.sub(r'\b' + drop + r'\b', '', n)
    return re.sub(r'[^a-z0-9]', '', n)

def parse_coord(val):
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, list) and len(val) > 0:
        return float(val[0])
    try:
        return float(val)
    except:
        return None

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_stops = json.load(f)

valid_osm = []
exact_osm_nodes = set()
for s in osm_stops:
    lat = parse_coord(s.get('latitude'))
    lon = parse_coord(s.get('longitude'))
    if lat and lon:
        s['lat_float'] = lat
        s['lon_float'] = lon
        valid_osm.append(s)
        exact_osm_nodes.add((round(lat, 5), round(lon, 5)))

matched_count = 0
unmatched = []

for p in profiles:
    p_lat = parse_coord(p['latitude'])
    p_lon = parse_coord(p['longitude'])
    coord = (round(p_lat, 5), round(p_lon, 5))
    if coord in exact_osm_nodes:
        matched_count += 1
    else:
        p_clean = clean_name(p['name'])
        best_dist = 999999
        best_osm = None
        for s in valid_osm:
            s_lat = s['lat_float']
            s_lon = s['lon_float']
            if abs(s_lat - p_lat) > 0.01 or abs(s_lon - p_lon) > 0.01:
                continue
            d = haversine(p_lat, p_lon, s_lat, s_lon)
            if d < 1000:
                s_clean = clean_name(s.get('name', ''))
                if p_clean in s_clean or s_clean in p_clean or (len(p_clean) > 4 and p_clean[:5] == s_clean[:5]):
                    if d < best_dist:
                        best_dist = d
                        best_osm = s
        unmatched.append((p['name'], p_lat, p_lon, best_dist, best_osm.get('name') if best_osm else None, best_osm.get('lat_float') if best_osm else None, best_osm.get('lon_float') if best_osm else None))

print(f"Stops already sitting EXACTLY on OSM node: {matched_count} / {len(profiles)}")
print(f"Stops not yet on exact OSM node: {len(unmatched)}")

close_unmatched = [u for u in unmatched if u[3] < 600]
print(f"Stops that have a named OSM match within 600m: {len(close_unmatched)}")
print("\nSample of close unmatched stops (with name match nearby):")
for u in close_unmatched[:20]:
    print(f"  '{u[0]}' -> '{u[4]}' (dist: {u[3]:.1f}m)")
