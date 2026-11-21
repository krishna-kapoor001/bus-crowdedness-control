import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

for target in ['aiims', 'anand vihar', 'nizamuddin', 'model town', 'rajghat', 'okhla industrial', 'mukarba', 'alipur', 'singhu', 'tuglakabad']:
    matches = [s['name'] for s in stops if target in s['name'].lower()]
    print(f"Target '{target}': {matches}")
