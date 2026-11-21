import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

stop_names_set = set(s['name'].lower().strip() for s in stops)

print(f"Total stops in stop_profiles.json: {len(stop_names_set)}")

for c in corridors:
    c_stops = c.get('stops', [])
    not_found = [s for s in c_stops if s.lower().strip() not in stop_names_set]
    if not_found:
        print(f"Corridor '{c['id']}' has stops NOT in stop_profiles.json: {not_found}")
