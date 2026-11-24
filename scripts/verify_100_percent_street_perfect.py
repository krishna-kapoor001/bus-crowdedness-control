import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def extract_coords(obj):
    lat = obj.get('latitude') or obj.get('lat')
    lon = obj.get('longitude') or obj.get('lon')
    if isinstance(lat, list) and isinstance(lon, list):
        if len(lat) > 0 and isinstance(lat[0], (int, float)):
            val1 = float(lat[0])
            val2 = float(lat[1]) if len(lat) > 1 else float(lon[0])
            if 28.0 <= val1 <= 29.0:
                return val1, val2
            elif 28.0 <= val2 <= 29.0:
                return val2, val1
    if isinstance(lat, (int, float)) and isinstance(lon, (int, float)):
        l1, l2 = float(lat), float(lon)
        if 28.0 <= l1 <= 29.0:
            return l1, l2
        elif 28.0 <= l2 <= 29.0:
            return l2, l1
    return None, None

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

osm_pts = []
for o in osm:
    tags = o.get('tags', {})
    if tags.get('railway') == 'platform':
        continue
    if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
        name = (o.get('name') or tags.get('name') or '').strip()
        if not name or name.lower() in ['unnamed']:
            continue
        lat, lon = extract_coords(o)
        if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
            osm_pts.append((lat, lon, name, tags))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog stops: {len(catalog)}")
print(f"Total authentic roadside OSM bus stops: {len(osm_pts)}")

perfect_count = 0
imperfect = []

for s in catalog:
    best_d = 999999
    best_o = None
    for lat, lon, name, tags in osm_pts:
        d = haversine(s['latitude'], s['longitude'], lat, lon)
        if d < best_d:
            best_d = d
            best_o = (lat, lon, name, tags)
            
    if best_d <= 1.0:
        perfect_count += 1
    else:
        imperfect.append((s['name'], best_d, s['latitude'], s['longitude'], best_o[2]))

print(f"\nStops dead-center on exact OSM roadside bus stop node (<= 1.0m): {perfect_count} / {len(catalog)} ({perfect_count/len(catalog)*100:.1f}%)")
print(f"Stops not exactly on node (> 1.0m): {len(imperfect)}")
for item in imperfect:
    print(f"  IMPERFECT: '{item[0]}' offset={item[1]:.1f}m to '{item[4]}'")

# Check pairwise collisions
collisions = []
for i in range(len(catalog)):
    for j in range(i + 1, len(catalog)):
        d = haversine(catalog[i]['latitude'], catalog[i]['longitude'], catalog[j]['latitude'], catalog[j]['longitude'])
        if d < 15.0:
            collisions.append((d, catalog[i]['name'], catalog[j]['name']))

print(f"\nCollisions (< 15m): {len(collisions)}")
for c in collisions:
    print(f"  COLLISION: {c[0]:.1f}m between '{c[1]}' and '{c[2]}'")
