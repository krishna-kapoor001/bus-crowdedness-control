import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    if c['id'] == 'corridor-airport':
        coords = c['coordinates']
        print(f"Total points: {len(coords)}")
        print("Point 0:", coords[0])
        print("Point 50:", coords[50])
        print("Point 100:", coords[100])
        print("Point 150:", coords[150])
        print("Point 200:", coords[200])
        print("Point 219:", coords[219])
