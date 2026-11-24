import json
import csv
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

# Also check GTFS stops
gtfs = []
with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        gtfs.append({
            'name': row['stop_name'],
            'lat': float(row['stop_lat']),
            'lon': float(row['stop_lon'])
        })

print(f"Total current stops: {len(stops)}")
print(f"Total OSM stops: {len(osm)}")
print(f"Total GTFS stops: {len(gtfs)}")

# Check GTFS direct name match
gtfs_map = {g['name'].lower().strip(): g for g in gtfs}
gtfs_matched = 0
gtfs_dist_errors = []
for s in stops:
    nl = s['name'].lower().strip()
    if nl in gtfs_map:
        gtfs_matched += 1
        g = gtfs_map[nl]
        d = haversine(s['latitude'], s['longitude'], g['lat'], g['lon'])
        gtfs_dist_errors.append((s['name'], d, s['latitude'], s['longitude'], g['lat'], g['lon']))

print(f"Direct GTFS name matches: {gtfs_matched} / {len(stops)}")
if gtfs_dist_errors:
    gtfs_dist_errors.sort(key=lambda x: x[1], reverse=True)
    print("\nTop 10 largest discrepancies between current coords and official GTFS:")
    for item in gtfs_dist_errors[:10]:
        print(f"  {item[0]}: diff = {item[1]:.1f}m (current: {item[2]:.5f}, {item[3]:.5f} vs GTFS: {item[4]:.5f}, {item[5]:.5f})")

# Check OSM matches
osm_map = {o['name'].lower().strip(): o for o in osm}
osm_matched = 0
osm_dist_errors = []
for s in stops:
    nl = s['name'].lower().strip()
    if nl in osm_map:
        osm_matched += 1
        o = osm_map[nl]
        d = haversine(s['latitude'], s['longitude'], o['latitude'], o['longitude'])
        osm_dist_errors.append((s['name'], d, s['latitude'], s['longitude'], o['latitude'], o['longitude']))

print(f"\nDirect OSM name matches: {osm_matched} / {len(stops)}")
if osm_dist_errors:
    osm_dist_errors.sort(key=lambda x: x[1], reverse=True)
    print("Top 10 largest discrepancies between current coords and OSM:")
    for item in osm_dist_errors[:10]:
        print(f"  {item[0]}: diff = {item[1]:.1f}m (current: {item[2]:.5f}, {item[3]:.5f} vs OSM: {item[4]:.5f}, {item[5]:.5f})")
