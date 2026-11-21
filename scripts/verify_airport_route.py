import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    if c['id'] == 'corridor-airport':
        print(f"ID: {c['id']}")
        print(f"Name: {c['name']}")
        print(f"Stops ({len(c['stops'])}): {c['stops']}")
        coords = c['coordinates']
        print(f"Total street coords: {len(coords)}")
        print(f"Start: {coords[0]}")
        print(f"End: {coords[-1]}")
        # Check if coordinates follow NH-48 and pass near Mahipalpur
        has_mahipalpur = any(28.54 <= pt[0] <= 28.55 and 77.12 <= pt[1] <= 77.13 for pt in coords)
        print(f"Passes through Mahipalpur: {has_mahipalpur}")
