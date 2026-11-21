import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

# Find all stops and see what tokens match in GTFS
for s in stops:
    words = [w for w in re.split(r'[\s/()\-]+', s.lower()) if len(w) > 3 and w not in ['road', 'village', 'metro', 'station', 'stand', 'stop', 'terminal', 'gate', 'nagar', 'vihar', 'enclave']]
    matches = []
    for g in gtfs:
        g_name = g['stop_name']
        g_lower = g_name.lower()
        if all(w in g_lower for w in words):
            matches.append((g_name, g['stop_lat'], g['stop_lon']))
    if not matches:
        print(f"NO TOKEN MATCH: '{s}' (tokens: {words})")
    elif len(matches) == 1:
        pass
    else:
        pass
