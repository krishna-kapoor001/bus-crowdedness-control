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

def normalize_stem(s):
    # Strip everything except letters and digits
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
            'stem': normalize_stem(name)
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

matched = []
unmatched = []

for s in stops:
    s_stem = normalize_stem(s['name'])
    best_osm = None
    best_dist = 999999
    
    if len(s_stem) >= 3:
        for o in osm_stops:
            # Bounding box 0.015 (~1.5 km)
            if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
                continue
            o_stem = o['stem']
            if len(o_stem) >= 3:
                # Check substring match without spaces
                if s_stem == o_stem or s_stem in o_stem or o_stem in s_stem or (len(s_stem) >= 5 and s_stem[:5] == o_stem[:5]):
                    d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
                    if d < 1200 and d < best_dist:
                        best_dist = d
                        best_osm = o
                        
    if best_osm:
        matched.append((s['name'], best_osm['name'], best_dist, s['latitude'], s['longitude'], best_osm['lat'], best_osm['lon']))
    else:
        unmatched.append(s)

print(f"Stops matched with stem normalization: {len(matched)} / {len(stops)}")
print(f"Remaining unmatched stops: {len(unmatched)}")

print("\nSample 30 newly matched stops (that previously failed):")
for m in [x for x in matched if x[2] > 20][:30]:
    print(f"  '{m[0]}' -> '{m[1]}' (moved {m[2]:.1f}m onto real OSM stop)")
