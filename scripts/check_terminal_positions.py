import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

# Find all stops with terminal, depot, stand, isbt, or is_major_hub
key_stops = []
for s in stops:
    name_low = s['name'].lower()
    if any(k in name_low for k in ['terminal', 'depot', 'isbt', 'stand']) or s.get('is_major_hub'):
        key_stops.append(s)

print(f"Total key terminals/depots/stands: {len(key_stops)}")
for s in key_stops[:40]:
    print(f"'{s['name']}': ({s['latitude']}, {s['longitude']}) - Hub: {s['is_major_hub']}")
