import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

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
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Find closest OSM stop for every single stop
closest_dists = []
for s in stops:
    min_d = 999999
    closest = None
    for o in osm_stops:
        if abs(s['latitude'] - o['lat']) > 0.01 or abs(s['longitude'] - o['lon']) > 0.01:
            continue
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < min_d:
            min_d = d
            closest = o
    closest_dists.append((min_d, s['name'], closest['name'] if closest else 'None', s))

within_30m = [c for c in closest_dists if c[0] <= 30]
within_60m = [c for c in closest_dists if 30 < c[0] <= 60]
within_100m = [c for c in closest_dists if 60 < c[0] <= 100]
within_250m = [c for c in closest_dists if 100 < c[0] <= 250]
farther_250m = [c for c in closest_dists if c[0] > 250]

print(f"Total stops: {len(stops)}")
print(f"Already within 30m of OSM stop: {len(within_30m)}")
print(f"Within 30m - 60m of OSM stop: {len(within_60m)}")
print(f"Within 60m - 100m of OSM stop: {len(within_100m)}")
print(f"Within 100m - 250m of OSM stop: {len(within_250m)}")
print(f"Farther than 250m (outer/rural): {len(farther_250m)}")
