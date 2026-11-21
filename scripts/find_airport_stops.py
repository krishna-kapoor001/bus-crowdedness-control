import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

for s in stops:
    if any(k in s['corridor'].lower() for k in ['airport', 'arterial']) or any(k in s['name'].lower() for k in ['dhaula kuan', 'satya niketan', 'mahipal', 'kapashera', 'shiv murti']):
        print(f"Name: '{s['name']}' | Corridor: '{s['corridor']}' | Coords: ({s['latitude']}, {s['longitude']})")
