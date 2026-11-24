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
    osm_raw = json.load(f)

named_osm = []
for o in osm_raw:
    name = (o.get('name') or '').strip()
    if not name or name.lower() in ['unnamed', 'bus stop']:
        continue
    lat, lon = extract_coords(o)
    if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        named_osm.append({'name': name, 'lat': lat, 'lon': lon, 'tags': o.get('tags', {})})

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

offset_stops = []
for s in catalog:
    best_d = 999999
    best_o = None
    for o in named_osm:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < best_d:
            best_d = d
            best_o = o
    if best_d > 0.5:
        offset_stops.append((s['name'], best_d, s['latitude'], s['longitude'], best_o['name'], best_o['lat'], best_o['lon']))

offset_stops.sort(key=lambda x: -x[1])
print(f"Stops with offset > 0.5m: {len(offset_stops)}")
for item in offset_stops[:20]:
    print(f"  '{item[0]}' offset={item[1]:.1f}m: ({item[2]}, {item[3]}) -> OSM: '{item[4]}' at ({item[5]}, {item[6]})")
