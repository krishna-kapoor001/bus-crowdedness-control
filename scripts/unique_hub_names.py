import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
names = sorted(list(set(h['name'] for h in hubs)))
print(f"Total unique major hub names: {len(names)}")
print(names)
