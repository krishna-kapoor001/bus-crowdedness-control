import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    print("=" * 60)
    print(f"ID: {c['id']}")
    print(f"Name: {c['name']}")
    print(f"Stops: {c.get('stops')}")
    coords = c.get('coordinates', [])
    print(f"Coords count: {len(coords)}")
    if coords:
        print(f"Start: {coords[0]} | End: {coords[-1]}")
