import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

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

hubs = [s for s in stops if s.get('is_major_hub', False)]

print(f"Auditing all {len(hubs)} Major Bus Stands against OSM ground-truth:")
perfect_hubs = 0
for h in hubs:
    min_d = min(haversine(h['latitude'], h['longitude'], o['lat'], o['lon']) for o in osm_stops)
    if min_d <= 1.0:
        perfect_hubs += 1
    else:
        print(f"  ! Hub '{h['name']}' is {min_d:.1f}m from nearest OSM node")

print(f"\nResult: {perfect_hubs} / {len(hubs)} Major Bus Stands are DEAD-CENTER (<= 1.0m) on exact OSM nodes! ({perfect_hubs/len(hubs)*100:.1f}%)")
