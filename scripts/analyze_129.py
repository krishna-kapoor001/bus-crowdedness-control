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

unmatched = [s for s in stops if norm(s) not in gtfs_norm]

print(f"Total unmatched: {len(unmatched)}")
for i, s in enumerate(unmatched):
    # Search GTFS stop names containing s or major part of s
    words = [w for w in re.findall(r'[a-zA-Z]{3,}', s) if w.lower() not in ['road', 'stop', 'stand', 'station', 'metro']]
    matches = []
    if words:
        for g in gtfs:
            g_low = g['stop_name'].lower()
            if all(w.lower() in g_low for w in words):
                matches.append(g['stop_name'])
    print(f"{i+1:3d}. '{s}' -> GTFS candidates: {matches[:3]}")
