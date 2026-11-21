import json

with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corrs = json.load(f)

for c in corrs:
    for s in c.get('stops', []):
        if 'crpf' in s.lower() or 'crown' in s.lower():
            print(f"Corridor ID: {c['id']}, Name: {c['name']}")
            print(f"Stops: {c['stops']}")
            print(f"Coordinates: {c['coordinates']}")
