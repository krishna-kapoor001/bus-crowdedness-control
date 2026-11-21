import json, math, os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open(os.path.join(DATA_DIR, 'osm_delhi_all_bus_stops.json'), 'r', encoding='utf-8') as f:
    osm_stops = json.load(f)

valid_osm = [s for s in osm_stops if isinstance(s.get('latitude'), (int, float)) and isinstance(s.get('longitude'), (int, float))]

print(f"Auditing {len(stops)} stops against {len(valid_osm)} verified OSM ground truth transit nodes...")

# 1. Check pairs between 60m and 100m
close_pairs = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if 60 <= d < 100:
            close_pairs.append((d, s1['name'], s2['name']))

close_pairs.sort(key=lambda x: x[0])
print(f"\n[PAIRS 60m-100m]: {len(close_pairs)} pairs found")
for d, n1, n2 in close_pairs[:25]:
    print(f"  {d:.1f}m: '{n1}' <-> '{n2}'")

# 2. Distance to nearest OSM ground truth stop
dist_distribution = {
    '< 25m': 0,
    '25-50m': 0,
    '50-100m': 0,
    '100-200m': 0,
    '> 200m': 0
}

far_stops = []
for s in stops:
    min_dist = float('inf')
    best_osm = None
    for o in valid_osm:
        d = haversine(s['latitude'], s['longitude'], o['latitude'], o['longitude'])
        if d < min_dist:
            min_dist = d
            best_osm = o
    
    if min_dist < 25:
        dist_distribution['< 25m'] += 1
    elif min_dist < 50:
        dist_distribution['25-50m'] += 1
    elif min_dist < 100:
        dist_distribution['50-100m'] += 1
    elif min_dist < 200:
        dist_distribution['100-200m'] += 1
    else:
        dist_distribution['> 200m'] += 1
        far_stops.append((s, min_dist, best_osm))

print("\n[DISTANCE TO NEAREST OSM GROUND-TRUTH TRANSIT NODE]:")
for bucket, count in dist_distribution.items():
    pct = (count / len(stops)) * 100
    print(f"  {bucket:>10}: {count:>5} stops ({pct:.1f}%)")

print(f"\n[STOPS > 200m FROM ANY OSM TRANSIT NODE]: {len(far_stops)}")
for s, d, o in far_stops[:25]:
    print(f"  {s['name']} at ({s['latitude']}, {s['longitude']}): nearest OSM '{o.get('name')}' is {d:.0f}m away")
