import json
import math

def dist(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1-a))

def parse_coord(val):
    if isinstance(val, (list, tuple)):
        return float(val[0])
    return float(val)

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    sp = json.load(f)

target_lat, target_lon = 28.679099, 77.20837

print("=== ALL OSM STOPS WITHIN 250M ===")
for o in osm:
    lat = parse_coord(o.get('latitude') or o.get('lat'))
    lon = parse_coord(o.get('longitude') or o.get('lon'))
    d = dist(target_lat, target_lon, lat, lon)
    if d < 250:
        print(f"d={d:.1f}m: name='{o.get('name')}', lat={lat}, lon={lon}, tags={o.get('tags')}")

print("\n=== ALL STOP_PROFILES STOPS WITHIN 250M ===")
for s in sp:
    lat = parse_coord(s.get('latitude'))
    lon = parse_coord(s.get('longitude'))
    d = dist(target_lat, target_lon, lat, lon)
    if d < 250:
        print(f"d={d:.1f}m: name='{s.get('name')}', lat={lat}, lon={lon}")
