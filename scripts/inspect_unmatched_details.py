import json
from collections import Counter

# Let's inspect the 481 unmatched stops from evaluate_perfect_osm_snapping.py
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

# Re-run matching to get the exact 481 unmatched
import math, re

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

unmatched = []
for s in stops:
    s_toks = clean_toks(s['name'])
    best_osm = None
    best_dist = 999999
    if s_toks:
        for o in osm_stops:
            if abs(s['latitude'] - o['lat']) > 0.015 or abs(s['longitude'] - o['lon']) > 0.015:
                continue
            if s_toks & o['toks']:
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
    if not best_osm:
        unmatched.append(s)

corr_counts = Counter(s.get('corridor') for s in unmatched)
print(f"Total unmatched stops: {len(unmatched)}")
print("Corridors of unmatched stops:")
for c, cnt in corr_counts.most_common():
    print(f"  {c}: {cnt}")

print("\nSample 30 unmatched stop names:")
for s in unmatched[:30]:
    print(f"  '{s['name']}' ({s['corridor']}) at ({s['latitude']}, {s['longitude']})")
