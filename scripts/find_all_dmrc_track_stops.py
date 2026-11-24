import json
import math

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

# Find all pure metro train stop_position nodes
metro_nodes = set()
for o in osm_raw:
    tags = o.get('tags', {})
    if tags.get('operator') == 'Delhi Metro Rail Corporation Limited':
        if tags.get('highway') != 'bus_stop':
            lat, lon = extract_coords(o)
            if lat and lon:
                metro_nodes.add((round(lat, 5), round(lon, 5)))

print(f"Total DMRC train stop_positions in OSM: {len(metro_nodes)}")

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    catalog = json.load(f)

metro_stops_in_catalog = []
for s in catalog:
    coord = (round(s['latitude'], 5), round(s['longitude'], 5))
    if coord in metro_nodes:
        metro_stops_in_catalog.append(s)

print(f"Catalog stops that are actually DMRC train positions on empty tracks/roads: {len(metro_stops_in_catalog)}")
for s in metro_stops_in_catalog:
    print(f"  METRO TRACK: '{s['name']}' at ({s['latitude']}, {s['longitude']}) - Hub: {s.get('is_major_hub')}")
