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

def normalize(name):
    clean = re.sub(r'[^a-zA-Z0-9]', ' ', name.lower())
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'near', 'opp', 'opposite', 'depot', 'isbt', 'dtc', 'cluster'}
    tokens = set(w for w in clean.split() if len(w) > 2 and w not in ignore)
    return tokens

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
            'tokens': normalize(name)
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total current stops: {len(stops)}")
print(f"Total named OSM stops: {len(osm_stops)}")

matches = []
for s in stops:
    s_toks = normalize(s['name'])
    if not s_toks:
        continue
    best_osm = None
    best_dist = 999999
    
    for o in osm_stops:
        overlap = s_toks & o['tokens']
        if overlap:
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            # Within 350m if matching key token, or within 500m if exact name match
            max_d = 500 if s['name'].lower() == o['name'].lower() else 350
            if d <= max_d and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm and best_dist > 3.0:
        matches.append((s['name'], best_osm['name'], best_dist, s['latitude'], s['longitude'], best_osm['lat'], best_osm['lon']))

print(f"Stops that can be snapped to OSM named icons: {len(matches)}")
print("\nSample 25 new snaps:")
for m in matches[:25]:
    print(f"  '{m[0]}' -> '{m[1]}' ({m[2]:.1f}m)")
