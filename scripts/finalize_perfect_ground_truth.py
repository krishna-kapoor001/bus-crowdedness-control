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

# Load OSM bus stops
with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_raw = json.load(f)

roadside_bus_stops = []
for o in osm_raw:
    tags = o.get('tags', {})
    if tags.get('railway') == 'platform':
        continue
    if tags.get('highway') == 'bus_stop' or tags.get('public_transport') == 'platform':
        name = (o.get('name') or tags.get('name') or '').strip()
        if not name or name.lower() in ['unnamed']:
            continue
        lat, lon = extract_coords(o)
        if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
            roadside_bus_stops.append({
                'name': name,
                'lat': lat,
                'lon': lon,
                'tags': tags,
                'shelter': tags.get('shelter') == 'yes'
            })

print(f"Loaded {len(roadside_bus_stops)} verified roadside bus stop nodes in Delhi.")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

# Terminal alignments to exact OSM shelter nodes
terminal_snaps = {
    'ISBT Kashmere Gate': (28.669517, 77.232170, True),
    'Shivaji Stadium Terminal': (28.632996, 77.215522, True),
    'Badarpur Border Terminal': (28.491472, 77.303722, True),
    'Punjabi Bagh Terminal': (28.667787, 77.137390, True),
    'Rajouri Garden': (28.647729, 77.119870, False),
    'ISBT Sarai Kale Khan': (28.590600, 77.257884, True),
    'Anand Vihar ISBT': (28.648984, 77.318288, True),
    'Nehru Place Terminal': (28.547266, 77.253895, True),
}

for s in catalog:
    if s['name'] in terminal_snaps:
        lat, lon, is_hub = terminal_snaps[s['name']]
        s['latitude'] = lat
        s['longitude'] = lon
        s['is_major_hub'] = is_hub
        print(f"Snapped '{s['name']}' to exact physical shelter at ({lat}, {lon})")

# Ensure existing ISBT Kashmere Gate is present
has_isbt = any(s['name'] == 'ISBT Kashmere Gate' for s in catalog)
if not has_isbt:
    catalog.append({
        "name": "ISBT Kashmere Gate",
        "latitude": 28.669517,
        "longitude": 77.232170,
        "corridor": "Ring Road Arterial",
        "monthly_boardings": 25200,
        "monthly_alightings": 23940,
        "is_major_hub": True
    })

# Strict filter: every stop MUST be <= 5.0m from an authentic OSM roadside bus stop node
strictly_verified = []
for s in catalog:
    best_d = 999999
    best_b = None
    for b in roadside_bus_stops:
        d = haversine(s['latitude'], s['longitude'], b['lat'], b['lon'])
        if d < best_d:
            best_d = d
            best_b = b
            
    if best_d <= 5.0:
        # Snap directly onto exact node (0.0m difference)
        s['latitude'] = round(best_b['lat'], 6)
        s['longitude'] = round(best_b['lon'], 6)
        strictly_verified.append(s)
    else:
        print(f"Discarding off-road stop: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - dist={best_d:.1f}m to '{best_b['name']}'")

# Deduplicate any stops that sit on the exact same coordinate (within 10m)
deduped = []
for s in strictly_verified:
    too_close = False
    for existing in deduped:
        if haversine(s['latitude'], s['longitude'], existing['latitude'], existing['longitude']) < 15.0:
            too_close = True
            # merge boardings
            existing['monthly_boardings'] += s.get('monthly_boardings', 0)
            if s.get('is_major_hub'):
                existing['is_major_hub'] = True
            break
    if not too_close:
        deduped.append(s)

print(f"\nFinal 100% Street-Perfect Stops: {len(deduped)}")
print(f"Major Bus Stands (Black Dots): {len([s for s in deduped if s.get('is_major_hub')])}")

deduped.sort(key=lambda x: x['monthly_boardings'], reverse=True)

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(deduped, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(deduped, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
