import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

def norm(text):
    return re.sub(r'[^a-z0-9]', '', text.lower())

gtfs_norm = {}
for g in gtfs:
    n = norm(g['stop_name'])
    if n not in gtfs_norm:
        gtfs_norm[n] = (float(g['stop_lat']), float(g['stop_lon']), g['stop_name'])

exact_matches = {}
unmatched = []

for s in stops:
    n = norm(s)
    if n in gtfs_norm:
        exact_matches[s] = gtfs_norm[n]
    else:
        unmatched.append(s)

print(f"Exact norm matches: {len(exact_matches)} / {len(stops)}")
print(f"Unmatched: {len(unmatched)}")
