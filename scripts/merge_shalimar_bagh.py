import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before merge: {len(stops)}")

sb_boardings = 0
sb_alightings = 0
merged = []

for s in stops:
    if s['name'] == 'Shalimar Bagh':
        sb_boardings = s.get('monthly_boardings', 0)
        sb_alightings = s.get('monthly_alightings', 0)
        continue
    merged.append(s)

for s in merged:
    if s['name'] == 'Shalimar Bagh A Block':
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + sb_boardings
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + sb_alightings

print(f"Stops count after merge: {len(merged)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(merged, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
