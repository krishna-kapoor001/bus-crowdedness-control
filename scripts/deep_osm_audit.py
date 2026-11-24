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
    return re.sub(r'[^a-z0-9]', '', (name or '').lower())

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

osm_stops = []
for o in osm_raw:
    name = (o.get('name') or '').strip()
    lat = parse_coord(o.get('latitude') or o.get('lat'))
    lon = parse_coord(o.get('longitude') or o.get('lon'))
    if 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        osm_stops.append({
            'name': name,
            'norm': normalize(name),
            'lat': lat,
            'lon': lon,
            'tags': o.get('tags', {}),
            'is_hub': o.get('is_hub', False)
        })

print(f"Total stops in profile: {len(stops)}")
print(f"Total OSM stops in bbox: {len(osm_stops)}")

# Check distance of each stop in profile to nearest OSM stop
unmatched = []
name_mismatch = []
matched_exact = []

for s in stops:
    s_norm = normalize(s['name'])
    best_dist = 999999
    best_osm = None
    for o in osm_stops:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < best_dist:
            best_dist = d
            best_osm = o
            
    if best_dist > 5.0:
        unmatched.append((s, best_dist, best_osm))
    else:
        # Check if name is similar
        if s_norm != best_osm['norm'] and s_norm not in best_osm['norm'] and best_osm['norm'] not in s_norm:
            name_mismatch.append((s, best_dist, best_osm))
        else:
            matched_exact.append((s, best_dist, best_osm))

print(f"\nExact name & coordinate matches (dist <= 5m): {len(matched_exact)}")
print(f"Coordinate matches (dist <= 5m) but different name: {len(name_mismatch)}")
print(f"Stops with dist > 5m to any OSM node: {len(unmatched)}")

if name_mismatch:
    print("\n--- SAMPLE NAME MISMATCHES (Stop vs OSM Node at same position) ---")
    for s, d, o in name_mismatch[:25]:
        print(f"Profile: '{s['name']}' at ({s['latitude']}, {s['longitude']}) vs OSM: '{o['name']}' (d={d:.1f}m)")

if unmatched:
    print("\n--- SAMPLE UNMATCHED (>5m from any OSM node) ---")
    for s, d, o in unmatched[:25]:
        print(f"Profile: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - nearest OSM is '{o['name']}' at {d:.1f}m")
