import json
import math
import re
import os

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

def clean_stem(s):
    s = re.sub(r'[^a-zA-Z0-9]', '', s.lower())
    for w in ['terminal', 'depot', 'busstop', 'busstand', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'isbt', 'dtc', 'cluster']:
        s = s.replace(w, '')
    return s

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
            'toks': clean_toks(name),
            'stem': clean_stem(name)
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total input stops: {len(stops)}")
print(f"Total authentic OSM stops: {len(osm_stops)}")

# Match and snap
perfect_stops = []
dropped_khaali_road = []

seen_osm_nodes = set()

for s in stops:
    s_toks = clean_toks(s['name'])
    s_stem = clean_stem(s['name'])
    best_osm = None
    best_dist = 999999
    
    # 1. Search by name tokens or stem within 1.5 km
    for o in osm_stops:
        if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
            continue
        
        is_match = False
        if s_toks and (s_toks & o['toks']):
            is_match = True
        elif len(s_stem) >= 4 and len(o['stem']) >= 4 and (s_stem in o['stem'] or o['stem'] in s_stem or s_stem[:5] == o['stem'][:5]):
            is_match = True
            
        if is_match:
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d < 1200 and d < best_dist:
                best_dist = d
                best_osm = o
                
    # 2. If no name match, check if literally sitting right next to an OSM bus stop (<= 45m)
    if not best_osm:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.001 or abs(s['longitude'] - o['lon']) > 0.001:
                continue
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d <= 45.0 and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm:
        # Snap directly onto authentic OSM node
        new_stop = dict(s)
        new_stop['latitude'] = round(best_osm['lat'], 6)
        new_stop['longitude'] = round(best_osm['lon'], 6)
        perfect_stops.append(new_stop)
    else:
        dropped_khaali_road.append(s)

print(f"\nAuthentic OSM-snapped stops: {len(perfect_stops)}")
print(f"Dropped khaali-road phantom stops: {len(dropped_khaali_road)}")

# Dedup: if multiple stops snapped to the exact same OSM node, merge their boardings
node_map = {}
for s in perfect_stops:
    node_key = (s['latitude'], s['longitude'])
    if node_key not in node_map:
        node_map[node_key] = s
    else:
        existing = node_map[node_key]
        existing['monthly_boardings'] = existing.get('monthly_boardings', 0) + s.get('monthly_boardings', 0)
        existing['monthly_alightings'] = existing.get('monthly_alightings', 0) + s.get('monthly_alightings', 0)

final_clean_stops = list(node_map.values())
final_clean_stops.sort(key=lambda x: x['monthly_boardings'], reverse=True)

print(f"Final 100% authentic, zero-duplicate, non-khaali-road stops: {len(final_clean_stops)}")

# Check distance between all pairs in final_clean_stops
close_pairs = []
for i in range(len(final_clean_stops)):
    for j in range(i + 1, len(final_clean_stops)):
        p1 = final_clean_stops[i]
        p2 = final_clean_stops[j]
        d = haversine(p1['latitude'], p1['longitude'], p2['latitude'], p2['longitude'])
        if d < 35:
            close_pairs.append((d, p1['name'], p2['name']))

print(f"Collisions (< 35m) in final catalog: {len(close_pairs)}")
