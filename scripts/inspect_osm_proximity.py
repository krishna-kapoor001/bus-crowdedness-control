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

# For each stop in stops, find the closest OSM stop regardless of name
distances = []
for s in stops:
    min_d = 999999
    closest = None
    for o in osm_stops:
        # Bounding box filter
        if abs(s['latitude'] - o['lat']) > 0.01 or abs(s['longitude'] - o['lon']) > 0.01:
            continue
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < min_d:
            min_d = d
            closest = o
    distances.append((min_d, s['name'], closest['name'] if closest else None))

distances.sort(key=lambda x: x[0])
print(f"Total stops: {len(stops)}")
print(f"Stops within 5 meters of an OSM named stop: {len([d for d in distances if d[0] <= 5])}")
print(f"Stops within 30 meters of an OSM named stop: {len([d for d in distances if d[0] <= 30])}")
print(f"Stops within 100 meters of an OSM named stop: {len([d for d in distances if d[0] <= 100])}")
print(f"Stops within 250 meters of an OSM named stop: {len([d for d in distances if d[0] <= 250])}")
print(f"Stops farther than 250m: {len([d for d in distances if d[0] > 250])}")

print("\nSample of stops with closest OSM stop (5m - 50m):")
for d in [x for x in distances if 5 < x[0] <= 50][:20]:
    print(f"  '{d[1]}' is {d[0]:.1f}m from OSM stop '{d[2]}'")
