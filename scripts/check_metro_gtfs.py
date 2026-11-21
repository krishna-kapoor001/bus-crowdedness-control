import csv

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

metro_stops = [r for r in gtfs if 'metro' in r['stop_name'].lower()]
print(f"Stops with 'Metro' in name: {len(metro_stops)}")
for s in metro_stops[:10]:
    print(f"  {s['stop_name']} -> ({s['stop_lat']}, {s['stop_lon']})")
