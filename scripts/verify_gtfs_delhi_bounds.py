import csv

# Delhi NCT strict boundary box:
# Min Lat: 28.404, Max Lat: 28.883
# Min Lon: 76.838, Max Lon: 77.348

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

outside_box = []
for r in gtfs:
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])
    name = r['stop_name']
    if not (28.40 <= lat <= 28.90 and 76.83 <= lon <= 77.35):
        outside_box.append((name, lat, lon))

print(f"Total stops evaluated: {len(gtfs)}")
print(f"Stops strictly outside Delhi NCT geographic box: {len(outside_box)}")
for o in outside_box:
    print("  Outside:", o)
