import csv

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    for g in csv.DictReader(f):
        if '28.668217' in g['stop_lat'] or '77.2253' in g['stop_lon']:
            print(g)
