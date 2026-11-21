import json
import urllib.request
import time

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops_data = json.load(f)

stops_map = {s['name'].lower().strip(): (s['latitude'], s['longitude']) for s in stops_data}

print(f"Loaded {len(stops_map)} stops.")

# Check corridor stops
with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    c_stops = c.get('stops', [])
    missing = []
    found_coords = []
    for s in c_stops:
        s_low = s.lower().strip()
        if s_low in stops_map:
            found_coords.append((s, stops_map[s_low]))
        else:
            missing.append(s)
    print(f"Corridor {c['id']}: {len(c_stops)} stops, {len(found_coords)} found, missing: {missing}")
