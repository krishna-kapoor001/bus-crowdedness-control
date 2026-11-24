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

def parse_coord(val):
    if isinstance(val, (list, tuple)):
        return float(val[0])
    return float(val)

def normalize(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Find any stop where another OSM node with the exact name exists between 5m and 60m
shifts = []
for s in stops:
    s_norm = normalize(s['name'])
    cands = []
    for o in osm:
        o_name = o.get('name') or ''
        if normalize(o_name) == s_norm:
            lat = parse_coord(o.get('latitude') or o.get('lat'))
            lon = parse_coord(o.get('longitude') or o.get('lon'))
            if 28.0 <= lat <= 29.0 and 76.5 <= lon <= 77.8:
                d = haversine(s['latitude'], s['longitude'], lat, lon)
                cands.append((d, lat, lon, o.get('tags', {})))
    cands.sort(key=lambda x: x[0])
    # If closest is > 5m away, or if there's a node between 5m and 50m that has shelter='yes' or operator
    if cands:
        closest_d = cands[0][0]
        # check if current is at cands[0] or if there is an alternate
        for d, lat, lon, tags in cands:
            if 10.0 <= d <= 60.0:
                shifts.append((s['name'], s['latitude'], s['longitude'], lat, lon, d, tags))

print(f"Total potential shifts found (nodes within 10-60m): {len(shifts)}")
for name, c_lat, c_lon, n_lat, n_lon, d, tags in shifts[:30]:
    print(f"'{name}': current=({c_lat}, {c_lon}) -> alternate=({n_lat}, {n_lon}) dist={d:.1f}m tags={tags}")
