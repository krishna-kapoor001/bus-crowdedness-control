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

# Group osm nodes by normalized name
osm_by_norm = {}
for o in osm:
    raw_name = o.get('name') or ''
    norm = normalize(raw_name)
    if not norm:
        continue
    lat = parse_coord(o.get('latitude') or o.get('lat'))
    lon = parse_coord(o.get('longitude') or o.get('lon'))
    if norm not in osm_by_norm:
        osm_by_norm[norm] = []
    osm_by_norm[norm].append({
        'name': raw_name,
        'lat': lat,
        'lon': lon,
        'tags': o.get('tags', {}),
        'is_hub': o.get('is_hub', False)
    })

print(f"Total stops in profile: {len(stops)}")
print(f"Total unique OSM normalized names: {len(osm_by_norm)}")

multi_nodes = []
for s in stops:
    s_norm = normalize(s['name'])
    candidates = osm_by_norm.get(s_norm, [])
    if len(candidates) > 1:
        # Check distances of all candidates to current s coordinates
        dists = [(haversine(s['latitude'], s['longitude'], c['lat'], c['lon']), c) for c in candidates]
        dists.sort(key=lambda x: x[0])
        # If the closest candidate is > 0.5m away OR if there is a candidate within 100m that has shelter/operator
        multi_nodes.append((s, dists))

print(f"Stops with multiple OSM nodes with same normalized name: {len(multi_nodes)}")
for s, dists in multi_nodes[:15]:
    print(f"\nStop '{s['name']}' at ({s['latitude']}, {s['longitude']}):")
    for d, c in dists:
        tags_str = f"shelter={c['tags'].get('shelter')}, op={c['tags'].get('operator')}"
        print(f"   d={d:.1f}m: ({c['lat']}, {c['lon']}) [{tags_str}]")
