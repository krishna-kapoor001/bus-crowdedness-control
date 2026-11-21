import json

with open('data/osm_delhi_all_bus_stops.json', encoding='utf-8') as f:
    osm_stops = json.load(f)

print(f"Total raw OSM bus stops: {len(osm_stops)}")

# Find OSM stops on or near NH-48 / Shiv Murti / Mahipalpur
nh48_osm = [s for s in osm_stops if 28.52 <= s['latitude'] <= 28.56 and 77.08 <= s['longitude'] <= 77.13]
print(f"OSM stops in NH-48 corridor: {len(nh48_osm)}")
for s in nh48_osm:
    print(f"  {s.get('name', 'Unnamed')}: ({s['latitude']}, {s['longitude']}) - tags: {s.get('tags', {})}")

# Find OSM stops along NH-24 / DME corridor
nh9_osm = [s for s in osm_stops if 28.61 <= s['latitude'] <= 28.635 and 77.27 <= s['longitude'] <= 77.34]
print(f"\nOSM stops in NH-9 corridor: {len(nh9_osm)}")
for s in nh9_osm[:15]:
    print(f"  {s.get('name', 'Unnamed')}: ({s['latitude']}, {s['longitude']}) - tags: {s.get('tags', {})}")
