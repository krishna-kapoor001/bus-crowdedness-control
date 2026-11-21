import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

for target in ['raj', 'hauz', 'mukarba', 'singhu', 'qut', 'cantt', 'tughlaq']:
    print(f"=== SEARCH '{target}' ===")
    for s in stops:
        if target in s['name'].lower():
            print(f"  '{s['name']}' -> ({s['latitude']}, {s['longitude']})")
