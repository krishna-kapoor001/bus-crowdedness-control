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

perfect_stops = []
for s in stops:
    s_toks = clean_toks(s['name'])
    s_stem = clean_stem(s['name'])
    best_osm = None
    best_dist = 999999
    
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
                
    if not best_osm:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.001 or abs(s['longitude'] - o['lon']) > 0.001:
                continue
            d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
            if d <= 45.0 and d < best_dist:
                best_dist = d
                best_osm = o
                
    if best_osm:
        new_stop = dict(s)
        new_stop['latitude'] = round(best_osm['lat'], 6)
        new_stop['longitude'] = round(best_osm['lon'], 6)
        perfect_stops.append(new_stop)

# Merge stops within 35 meters (opposite sides of the road / duplicate platforms)
merged_catalog = []
for s in sorted(perfect_stops, key=lambda x: x['monthly_boardings'], reverse=True):
    # Check if close to an already accepted stop
    matched_existing = None
    for ex in merged_catalog:
        d = haversine(s['latitude'], s['longitude'], ex['latitude'], ex['longitude'])
        if d < 35.0:
            matched_existing = ex
            break
    if matched_existing:
        matched_existing['monthly_boardings'] += s.get('monthly_boardings', 0)
        matched_existing['monthly_alightings'] += s.get('monthly_alightings', 0)
    else:
        merged_catalog.append(s)

print(f"Total authentic OSM-verified stops: {len(merged_catalog)}")

# Ensure Hansraj College is present
has_hansraj = any('hansraj' in s['name'].lower() for s in merged_catalog)
print("Hansraj College present:", has_hansraj)

# Ensure Saket Bus Stop and Dhaula Kuan are present
has_saket = any('saket' in s['name'].lower() for s in merged_catalog)
has_dhaula = any('dhaula' in s['name'].lower() for s in merged_catalog)
print("Saket present:", has_saket, "Dhaula Kuan present:", has_dhaula)

# Backup current files first
with open('data/processed/stop_profiles_backup.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2)

# Write updated clean catalog
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(merged_catalog, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(merged_catalog, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
