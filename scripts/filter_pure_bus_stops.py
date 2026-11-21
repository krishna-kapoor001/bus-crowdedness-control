import json

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    raw = json.load(f)

pure_bus_stops = []
for s in raw:
    tags = s.get('tags', {})
    hway = tags.get('highway')
    amen = tags.get('amenity')
    pub = tags.get('public_transport')
    op = tags.get('operator', '').lower()
    
    # Exclude metro, railway, trains
    if 'metro' in op or 'railway' in op or 'indian railways' in op:
        continue
    if pub == 'stop_position':
        continue # train/metro track stop positions!
    if hway != 'bus_stop' and amen != 'bus_station' and pub != 'platform':
        continue
        
    lat = s['latitude']
    lon = s['longitude']
    if isinstance(lat, list) or isinstance(lon, list): continue
    
    # Strictly Delhi NCT
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        continue
        
    # Exclude Haryana/UP operators
    if 'gurugram' in op or 'gmcbl' in op or 'noida' in op or 'upsrtc' in op or 'ghaziabad' in op:
        continue
        
    name = s['name'].strip()
    if not name or name.lower() == 'unnamed':
        continue
        
    pure_bus_stops.append(s)

print(f"Total REAL Pure Delhi Bus Stops in OSM: {len(pure_bus_stops)}")
hubs = [s for s in pure_bus_stops if s['is_hub']]
local = [s for s in pure_bus_stops if not s['is_hub']]
print(f"  Major Bus Stands / Terminals: {len(hubs)}")
print(f"  Regular Bus Stops: {len(local)}")

for s in pure_bus_stops[:20]:
    print(f"  • '{s['name']}': [{s['latitude']}, {s['longitude']}] | {s['tags']}")
