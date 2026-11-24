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

def get_tokens(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', (name or '').lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'road', 'marg', 'delhi', 'village', 'cluster', 'depot', 'cws', 'ii', 'iv'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

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
            'tokens': get_tokens(name),
            'lat': lat,
            'lon': lon,
            'tags': o.get('tags', {}),
            'is_hub': o.get('is_hub', False)
        })

print(f"Total catalog stops: {len(stops)}")
print(f"Total named OSM stops: {len(osm_stops)}")

# Find which stops in our catalog have NO matching named OSM stop within 100m
has_matching_osm_stop = []
no_matching_osm_stop = []

for s in stops:
    s_toks = get_tokens(s['name'])
    best_match = None
    best_dist = 999999
    
    # Check if there is an OSM stop within 100m with overlapping name tokens
    for o in osm_stops:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d <= 120.0:
            # Check token overlap or substring match
            overlap = s_toks & o['tokens']
            is_sub = (s['name'].lower() in o['name'].lower()) or (o['name'].lower() in s['name'].lower())
            if overlap or is_sub:
                if d < best_dist:
                    best_dist = d
                    best_match = o
                    
    if best_match:
        has_matching_osm_stop.append((s, best_dist, best_match))
    else:
        # Find closest OSM stop of ANY name
        closest_any = min(osm_stops, key=lambda o: haversine(s['latitude'], s['longitude'], o['lat'], o['lon']))
        d_any = haversine(s['latitude'], s['longitude'], closest_any['lat'], closest_any['lon'])
        no_matching_osm_stop.append((s, d_any, closest_any))

print(f"\nStops with matching named OSM bus stop icon nearby: {len(has_matching_osm_stop)}")
print(f"Stops with NO matching named OSM bus stop icon within 120m: {len(no_matching_osm_stop)}")

print("\n--- ALL STOPS WITH NO MATCHING OSM BUS STOP ICON ---")
for s, d, o in no_matching_osm_stop:
    print(f"  '{s['name']}' at ({s['latitude']}, {s['longitude']}) - Nearest OSM has DIFFERENT name: '{o['name']}' at {d:.1f}m")
