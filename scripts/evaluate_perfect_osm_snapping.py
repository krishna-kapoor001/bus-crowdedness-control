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

print(f"Total current stops: {len(stops)}")
print(f"Total authentic OSM bus stops: {len(osm_stops)}")

# Match each stop in stops to the best authentic OSM bus stop
matched_stops = []
unmatched_stops = []

for s in stops:
    s_toks = clean_toks(s['name'])
    best_osm = None
    best_dist = 999999
    
    # 1. Exact or token name match within 1200m
    if s_toks:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
                continue
            overlap = s_toks & o['toks']
            if overlap:
                d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
                if d < 1200 and d < best_dist:
                    best_dist = d
                    best_osm = o
                    
    # 2. If no name match, check if physical stop is within 45m (same physical shelter)
    if not best_osm:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.001 or abs(s['longitude'] - o['lon']) > 0.001:
                continue
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d <= 45.0 and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm:
        matched_stops.append({
            'orig_name': s['name'],
            'osm_name': best_osm['name'],
            'dist': best_dist,
            'orig_lat': s['latitude'],
            'orig_lon': s['longitude'],
            'osm_lat': best_osm['lat'],
            'osm_lon': best_osm['lon'],
            'stop_obj': s
        })
    else:
        unmatched_stops.append(s)

print(f"\nStops that have an authentic OSM bus stop match: {len(matched_stops)}")
print(f"Stops that have NO OSM bus stop (on khaali road): {len(unmatched_stops)}")
