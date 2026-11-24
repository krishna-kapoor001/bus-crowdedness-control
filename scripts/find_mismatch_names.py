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
    if 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6 and name:
        osm_stops.append({
            'name': name,
            'norm': normalize(name),
            'lat': lat,
            'lon': lon,
            'tags': o.get('tags', {}),
            'is_hub': o.get('is_hub', False)
        })

# Check for each catalog stop what OSM node it sits on
mismatches = []
far_away = []

for s in stops:
    best_d = 999999
    best_o = None
    for o in osm_stops:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < best_d:
            best_d = d
            best_o = o
            
    if best_d > 25.0:
        far_away.append((s, best_d, best_o))
    elif best_d <= 5.0:
        s_norm = normalize(s['name'])
        o_norm = best_o['norm']
        # If norms have no common substring of length >= 4
        common = False
        for sz in range(5, min(len(s_norm), len(o_norm)) + 1):
            for i in range(len(s_norm) - sz + 1):
                if s_norm[i:i+sz] in o_norm:
                    common = True
                    break
            if common:
                break
        if not common:
            mismatches.append((s, best_d, best_o))

print(f"Total catalog stops: {len(stops)}")
print(f"Far away (> 25m from ANY OSM bus stop): {len(far_away)}")
for s, d, o in far_away:
    print(f"  FAR: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - dist={d:.1f}m to '{o['name']}'")

print(f"\nCompletely different name at exact same node (dist <= 5m): {len(mismatches)}")
for s, d, o in mismatches[:35]:
    print(f"  DIFF NAME: Catalog '{s['name']}' vs OSM Tile '{o['name']}' (d={d:.1f}m)")
