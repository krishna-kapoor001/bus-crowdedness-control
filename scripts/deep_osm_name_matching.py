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

def clean_toks(s):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', s.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'near', 'opp', 'opposite', 'depot', 'isbt', 'dtc', 'cluster', 'colony', 'block', 'phase', 'sec', 'sector', 'hub'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

osm_stops = []
for o in osm_raw:
    name = (o.get('name') or '').strip()
    if not name or name.lower() == 'unnamed':
        continue
    lat = o.get('latitude')
    lon = o.get('longitude')
    if isinstance(lat, list) and len(lat) == 2:
        lon, lat = lat[0], lat[1]
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        osm_stops.append({
            'name': name,
            'lat': float(lat),
            'lon': float(lon),
            'toks': clean_toks(name)
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

name_matched_snaps = []
no_osm_match_stops = []

for s in stops:
    # Check if already within 20m of an OSM stop
    min_d = 999999
    closest_any = None
    for o in osm_stops:
        if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
            continue
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < min_d:
            min_d = d
            closest_any = o
            
    if min_d <= 20.0:
        continue # Already sitting right on an OSM stop!
        
    # Otherwise, search by name tokens within 1.5 km
    s_toks = clean_toks(s['name'])
    best_osm = None
    best_dist = 999999
    if s_toks:
        for o in osm_stops:
            overlap = s_toks & o['toks']
            if overlap:
                # check bounding box 0.015 (~1.5 km)
                if abs(s['latitude'] - o['lat']) > 0.02 or abs(s['longitude'] - o['lon']) > 0.02:
                    continue
                d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
                if d < 1200 and d < best_dist:
                    best_dist = d
                    best_osm = o
                    
    if best_osm:
        name_matched_snaps.append((s['name'], best_osm['name'], best_dist, s['latitude'], s['longitude'], best_osm['lat'], best_osm['lon']))
    else:
        no_osm_match_stops.append((min_d, s['name'], s['corridor'], s['latitude'], s['longitude']))

print(f"Stops that can be snapped to OSM by name (up to 1.2km): {len(name_matched_snaps)}")
print(f"Stops with NO named OSM stop nearby (truly empty road / outer): {len(no_osm_match_stops)}")

print("\nSample 25 name-matched snaps:")
for n in name_matched_snaps[:25]:
    print(f"  '{n[0]}' -> '{n[1]}' (distance: {n[2]:.1f}m)")

print("\nSample 25 stops with NO OSM match:")
for u in no_osm_match_stops[:25]:
    print(f"  '{u[1]}' ({u[2]}): {u[0]:.1f}m from any OSM stop (lat: {u[3]}, lon: {u[4]})")
