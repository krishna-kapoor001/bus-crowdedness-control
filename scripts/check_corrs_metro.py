import json

with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corrs = json.load(f)

for c in corrs:
    for s in c.get('stops', []):
        if 'metro' in s.lower():
            print(f"Corridor '{c['id']}' ({c['name']}): '{s}'")
