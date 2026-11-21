import csv
import gzip
import re

# Load all stop names from gtfs
with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs_stops = list(csv.DictReader(f))
gtfs_names = set(r['stop_name'].strip() for r in gtfs_stops)
print(f"Total unique stop names in GTFS: {len(gtfs_names)}")

# Check stop names in raw October-Delhi.csv
raw_stops = set()
with open('data/raw/October-Delhi.csv', 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.DictReader(f)
    for i, row in enumerate(reader):
        start = row.get('start_stop_name')
        end = row.get('end_stop_name')
        if start: raw_stops.add(start.strip())
        if end: raw_stops.add(end.strip())
        if i >= 100000: # sample 100k
            break

print(f"Unique stop names in first 100k raw tickets: {len(raw_stops)}")
overlap = raw_stops.intersection(gtfs_names)
print(f"Direct exact match overlap: {len(overlap)} / {len(raw_stops)}")
