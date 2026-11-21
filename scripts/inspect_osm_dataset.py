import json

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm_stops = json.load(f)

print(f"Total extracted OSM stops in New Delhi region: {len(osm_stops)}")

# Check Yamuna Vihar
yv = [s for s in osm_stops if 'yamuna vihar' in s['name'].lower()]
print(f"\nYamuna Vihar OSM stops ({len(yv)}):")
for s in yv:
    print(f"  - '{s['name']}': [{s['latitude']}, {s['longitude']}] (Hub: {s['is_hub']})")

# Check Shahdara
sh = [s for s in osm_stops if 'shahdara' in s['name'].lower()]
print(f"\nShahdara OSM stops ({len(sh)}):")
for s in sh:
    print(f"  - '{s['name']}': [{s['latitude']}, {s['longitude']}] (Hub: {s['is_hub']})")

# Check Kashmiri Gate / ISBT
isbt = [s for s in osm_stops if 'isbt' in s['name'].lower() or 'kashmere' in s['name'].lower() or 'kashmiri' in s['name'].lower()]
print(f"\nISBT / Kashmere Gate OSM stops ({len(isbt)}):")
for s in isbt[:10]:
    print(f"  - '{s['name']}': [{s['latitude']}, {s['longitude']}] (Hub: {s['is_hub']})")
