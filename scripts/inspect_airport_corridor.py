import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    if c['id'] == 'corridor-airport':
        coords = c['coordinates']
        print(f"Total coords: {len(coords)}")
        print("First 5 coords:", coords[:5])
        print("Middle 5 coords:", coords[len(coords)//2 - 2 : len(coords)//2 + 3])
        print("Last 5 coords:", coords[-5:])
