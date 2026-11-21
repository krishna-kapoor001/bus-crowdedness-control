import csv
import json
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

for s in stops:
    s_low = s.lower().strip()
    norm_s = re.sub(r'[^a-z0-9]', '', s_low)
    
    # Check if exact
    exact = [g for g in gtfs if re.sub(r'[^a-z0-9]', '', g['stop_name'].lower()) == norm_s]
    if not exact:
        # Search GTFS for close candidates
        candidates = []
        # Key tokens
        tokens = [w for w in re.split(r'[\s/()\-]+', s_low) if len(w) >= 3 and w not in ['road', 'terminal', 'station', 'metro', 'crossing', 'stand', 'stop', 'gate']]
        if tokens:
            for g in gtfs:
                g_name = g['stop_name']
                g_low = g_name.lower()
                if any(t in g_low for t in tokens):
                    candidates.append((g['stop_name'], g['stop_lat'], g['stop_lon']))
        print(f"STOP: '{s}' -> {len(candidates)} candidates")
        for c in candidates[:3]:
            print(f"    '{c[0]}' -> ({c[1]}, {c[2]})")
