import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops in network: {len(stops)}")

# Find which stops in gtfs match the exact or near-exact coordinates
for s in stops:
    name = s['name']
    lat, lon = s['latitude'], s['longitude']
    matched_gtfs = []
    for g in gtfs:
        try:
            g_lat, g_lon = float(g['stop_lat']), float(g['stop_lon'])
            if abs(g_lat - lat) < 0.0002 and abs(g_lon - lon) < 0.0002:
                matched_gtfs.append(g['stop_name'])
        except:
            pass
    # If the stop name doesn't share any word with matched_gtfs name, it's a BAD match!
    name_words = set(re.findall(r'\b[a-z]{3,}\b', name.lower()))
    gtfs_words = set(re.findall(r'\b[a-z]{3,}\b', " ".join(matched_gtfs).lower())) if matched_gtfs else set()
    common = name_words.intersection(gtfs_words)
    if not common:
        print(f"SUSPICIOUS / MISMATCHED: '{name}' ({lat}, {lon}) matched GTFS stop(s): {matched_gtfs[:3]}")
