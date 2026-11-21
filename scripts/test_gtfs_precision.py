import csv
import json

gtfs_stops = []
with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        gtfs_stops.append({
            'name': row['stop_name'],
            'lat': float(row['stop_lat']),
            'lon': float(row['stop_lon'])
        })

targets = [
    'kalkaji temple', 'mayur vihar phase 1', 'laxmi nagar', 'seelampur',
    'pahar gunj', 'madangir', 'badli crossing', 'alipur', 'dabri crossing', 'tughlaqabad'
]

for t in targets:
    matches = [g for g in gtfs_stops if t in g['name'].lower()]
    print(f"\nTarget '{t}':")
    for m in matches[:3]:
        print(f"  GTFS: '{m['name']}' -> ({m['lat']}, {m['lon']})")
