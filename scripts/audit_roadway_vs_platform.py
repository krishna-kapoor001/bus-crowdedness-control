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

# Group OSM nodes: which ones are physical bus stops (highway=bus_stop) vs in-roadway stop_positions?
osm_nodes = []
for o in osm_raw:
    lat, lon = extract_coords(o)
    if lat and lon and 28.3 <= lat <= 29.0 and 76.8 <= lon <= 77.6:
        tags = o.get('tags', {})
        name = (o.get('name') or tags.get('name') or '').strip()
        is_highway_stop = (tags.get('highway') == 'bus_stop')
        is_platform = (tags.get('public_transport') == 'platform')
        is_stop_position = (tags.get('public_transport') == 'stop_position')
        has_shelter = (tags.get('shelter') == 'yes')
        osm_nodes.append({
            'name': name,
            'lat': lat,
            'lon': lon,
            'tags': tags,
            'is_highway_stop': is_highway_stop,
            'is_platform': is_platform,
            'is_stop_position': is_stop_position,
            'has_shelter': has_shelter
        })

print(f"Total OSM nodes parsed: {len(osm_nodes)}")
print(f"  highway=bus_stop: {len([x for x in osm_nodes if x['is_highway_stop']])}")
print(f"  public_transport=platform: {len([x for x in osm_nodes if x['is_platform']])}")
print(f"  public_transport=stop_position (in roadway): {len([x for x in osm_nodes if x['is_stop_position']])}")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

print(f"\nTotal catalog stops: {len(catalog)}")

snapped_to_roadway = []
snapped_to_highway_stop = []
snapped_to_unnamed = []

for s in catalog:
    # Find exact matching node (d <= 1.0m)
    matched = None
    for o in osm_nodes:
        d = haversine(s['latitude'], s['longitude'], o['lat'], o['lon'])
        if d <= 1.5:
            matched = o
            break
            
    if matched:
        if matched['is_stop_position'] and not matched['is_highway_stop']:
            snapped_to_roadway.append((s, matched))
        elif matched['is_highway_stop'] or matched['is_platform']:
            snapped_to_highway_stop.append((s, matched))
        if not matched['name'] or matched['name'].lower() in ['unnamed', 'bus stop']:
            snapped_to_unnamed.append((s, matched))
    else:
        snapped_to_roadway.append((s, None))

print(f"\nCatalog stops sitting on physical highway=bus_stop / platform: {len(snapped_to_highway_stop)}")
print(f"Catalog stops sitting on in-roadway stop_position (bare road): {len(snapped_to_roadway)}")
print(f"Catalog stops sitting on unnamed OSM nodes: {len(snapped_to_unnamed)}")

if snapped_to_roadway:
    print("\n--- SAMPLE STOPS ON IN-ROADWAY STOP_POSITION (BARE ROAD) ---")
    for s, m in snapped_to_roadway[:25]:
        m_tags = m['tags'] if m else 'NO_MATCH'
        print(f"  '{s['name']}' at ({s['latitude']}, {s['longitude']}) - tags: {m_tags}")
