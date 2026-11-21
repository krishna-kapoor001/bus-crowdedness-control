import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    coords = c.get('coordinates', [])
    print(f"ID: {c['id']} | Name: {c['name']} | Coords Count: {len(coords)} | Stops: {c.get('stops')}")
    if coords and len(coords) < 10:
        print("  Sample coords:", coords)
