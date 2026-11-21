import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
print('Total stops:', len(stops))
print('Total hubs (black dots):', len(hubs))
for h in hubs:
    print(f"  {h['name']}: ({h['latitude']}, {h['longitude']}) - {h.get('corridor')}")
