import json
import math

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

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

osm_pts = []
for o in osm:
    lat = parse_coord(o.get('latitude') or o.get('lat'))
    lon = parse_coord(o.get('longitude') or o.get('lon'))
    name = (o.get('name') or '').strip()
    if 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        osm_pts.append((lat, lon, name, o.get('tags', {})))

print(f"Loaded {len(stops)} stops and {len(osm_pts)} OSM points.")

distance_buckets = {
    '0 - 2m': [],
    '2 - 10m': [],
    '10 - 30m': [],
    '30 - 100m': [],
    '> 100m': []
}

for s in stops:
    best_d = 999999
    best_o = None
    for lat, lon, name, tags in osm_pts:
        d = haversine(s['latitude'], s['longitude'], lat, lon)
        if d < best_d:
            best_d = d
            best_o = (lat, lon, name, tags)
            
    if best_d <= 2.0:
        distance_buckets['0 - 2m'].append((s, best_d, best_o))
    elif best_d <= 10.0:
        distance_buckets['2 - 10m'].append((s, best_d, best_o))
    elif best_d <= 30.0:
        distance_buckets['10 - 30m'].append((s, best_d, best_o))
    elif best_d <= 100.0:
        distance_buckets['30 - 100m'].append((s, best_d, best_o))
    else:
        distance_buckets['> 100m'].append((s, best_d, best_o))

for bucket, items in distance_buckets.items():
    print(f"Bucket {bucket}: {len(items)} stops")

print("\n--- ALL STOPS WITH DISTANCE > 10m TO ANY OSM BUS STOP ---")
for s, d, o in distance_buckets['10 - 30m'] + distance_buckets['30 - 100m'] + distance_buckets['> 100m']:
    print(f"'{s['name']}' at ({s['latitude']}, {s['longitude']}) - dist={d:.1f}m to nearest OSM '{o[2]}'")
