import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

for s in stops:
    if 'anand vihar' in s['name'].lower():
        print(s)
