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

def extract_coords(obj):
    lat = obj.get('latitude') or obj.get('lat')
    lon = obj.get('longitude') or obj.get('lon')
    if isinstance(lat, list) and isinstance(lon, list):
        # Could be [lon, lat] list
        if len(lat) > 0 and isinstance(lat[0], (int, float)):
            # check which is lat and which is lon
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

named_osm_stops = []
for o in osm_raw:
    name = (o.get('name') or '').strip()
    if not name or name.lower() in ['unnamed', 'bus stop']:
        continue
    lat, lon = extract_coords(o)
    if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        tags = o.get('tags', {})
        named_osm_stops.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'tags': tags
        })

print(f"Total authentic named OSM bus stops in Delhi: {len(named_osm_stops)}")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Total catalog stops: {len(catalog)}")

suspicious_stops = []
for s in catalog:
    # Find nearest named OSM stop
    best_d = 999999
    best_o = None
    for o in named_osm_stops:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d < best_d:
            best_d = d
            best_o = o
            
    if best_d > 20.0:
        suspicious_stops.append((s, best_d, best_o))

print(f"\nStops > 20m away from ANY named OSM bus stop: {len(suspicious_stops)}")
for s, d, o in suspicious_stops:
    print(f"  '{s['name']}' at ({s['latitude']}, {s['longitude']}): dist={d:.1f}m to '{o['name']}' at ({o['lat']}, {o['lon']})")
