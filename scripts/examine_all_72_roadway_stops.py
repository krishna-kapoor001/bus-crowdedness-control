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

# Index all OSM nodes
all_osm = []
for o in osm_raw:
    lat, lon = extract_coords(o)
    if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        all_osm.append({
            'name': (o.get('name') or o.get('tags', {}).get('name') or '').strip(),
            'lat': lat,
            'lon': lon,
            'tags': o.get('tags', {})
        })

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"Examining all {len(catalog)} catalog stops...")

roadway_stops = []
for s in catalog:
    # Find exact matching node (d <= 1.5m)
    exact_o = None
    for o in all_osm:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d <= 1.5:
            exact_o = o
            break
            
    if exact_o and exact_o['tags'].get('public_transport') == 'stop_position' and exact_o['tags'].get('highway') != 'bus_stop':
        # Find ANY nearby highway=bus_stop or platform within 150m
        nearby_platforms = []
        for o in all_osm:
            if o['tags'].get('highway') == 'bus_stop' or o['tags'].get('public_transport') == 'platform':
                d_p = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
                if d_p <= 120.0:
                    nearby_platforms.append((d_p, o))
        nearby_platforms.sort(key=lambda x: x[0])
        roadway_stops.append((s, exact_o, nearby_platforms))

print(f"\nTotal stops sitting on pure stop_position (in roadway): {len(roadway_stops)}")
for s, exact_o, nearby in roadway_stops:
    op = exact_o['tags'].get('operator', 'None')
    best_p_str = f"Nearest platform: '{nearby[0][1]['name']}' at {nearby[0][0]:.1f}m" if nearby else "NO NEARBY PLATFORM"
    print(f"  '{s['name']}' at ({s['latitude']}, {s['longitude']}) [op={op}] -> {best_p_str}")
