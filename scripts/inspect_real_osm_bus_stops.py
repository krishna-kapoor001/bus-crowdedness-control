import json

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

print(f"Total in osm_delhi_all_bus_stops.json: {len(osm)}")

# Filter strictly for Delhi NCT
delhi_osm = []
for s in osm:
    lat = s['latitude']
    lon = s['longitude']
    if isinstance(lat, list) or isinstance(lon, list): continue
    if 28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35:
        name = s['name'].strip()
        if name and name.lower() != 'unnamed':
            delhi_osm.append(s)

print(f"Named OSM bus stops in Delhi NCT: {len(delhi_osm)}")
for s in delhi_osm[:15]:
    print(f"  - '{s['name']}': [{s['latitude']}, {s['longitude']}] | {s['tags']}")
