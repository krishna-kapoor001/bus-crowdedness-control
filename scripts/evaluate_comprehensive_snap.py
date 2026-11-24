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
    ignore = {'bus', 'stop', 'stand', 'terminal', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'near', 'opp', 'opposite', 'depot', 'isbt', 'dtc', 'cluster', 'colony', 'block', 'phase', 'sec', 'sector'}
    return set(w for w in clean.split() if len(w) > 2 and w not in ignore)

def clean_str(s):
    s = s.lower()
    for w in ['terminal', 'depot', 'bus stop', 'bus stand', 'crossing', 'xing', 'more', 'mor', 'road', 'marg', 'delhi', 'village', 'isbt', 'dtc']:
        s = re.sub(r'\b' + w + r'\b', '', s)
    return re.sub(r'[^a-z0-9]', '', s)

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
            'clean': clean_str(name)
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total current stops: {len(stops)}")

snaps = []
for s in stops:
    s_toks = clean_toks(s['name'])
    s_clean = clean_str(s['name'])
    
    best_osm = None
    best_dist = 999999
    
    for o in osm_stops:
        if abs(s['latitude'] - o['lat']) > 0.005 or abs(s['longitude'] - o['lon']) > 0.005:
            continue
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        
        # Criteria 1: Exact or high string match within 180m
        is_name_match = False
        if s_clean and o['clean'] and (s_clean == o['clean'] or s_clean in o['clean'] or o['clean'] in s_clean):
            is_name_match = True
        elif len(s_toks & o['toks']) >= 1:
            is_name_match = True
        elif d <= 15.0: # If literally within 15 meters, it is the same physical stop shelter!
            is_name_match = True
            
        if is_name_match:
            max_dist = 220 if (s_clean == o['clean'] or (s_toks and s_toks == o['toks'])) else 120
            if d <= max_dist and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm and best_dist > 1.0: # if not already within 1m
        snaps.append((s['name'], best_osm['name'], best_dist, s['latitude'], s['longitude'], best_osm['lat'], best_osm['lon']))

print(f"Total stops to snap onto exact OSM tile icons: {len(snaps)}")
print("\nSample 25 snaps:")
for sn in snaps[:25]:
    print(f"  '{sn[0]}' -> '{sn[1]}' (moved {sn[2]:.1f}m onto OSM icon)")
