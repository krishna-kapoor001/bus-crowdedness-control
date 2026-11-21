import json

with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

print(f"Total stops in stop_profiles.json: {len(stops)}")
for idx, s in enumerate(stops):
    if 'Shahdara' in s.get('name', ''):
        print(f"Index {idx}: {s.get('name')}, lat={s.get('latitude')}, lon={s.get('longitude')}, is_hub={s.get('is_major_hub')}")
