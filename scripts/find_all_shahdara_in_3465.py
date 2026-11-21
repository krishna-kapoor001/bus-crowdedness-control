import json

with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

print("All stops with Shahdara:")
for s in stops:
    if 'shahdara' in s['name'].lower():
        print(" ", s['name'], s['latitude'], s['longitude'], s['is_major_hub'])
