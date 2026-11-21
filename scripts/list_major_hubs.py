import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
print(f"Total major hubs (black dots): {len(hubs)}")
for h in hubs[:30]:
    print(f"'{h['name']}': ({h['latitude']}, {h['longitude']})")
