import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")
for i, s in enumerate(stops[:35]):
    print(f"{i+1}. {s['name']} -> ({s['latitude']}, {s['longitude']}) | hub={s['is_major_hub']}")
