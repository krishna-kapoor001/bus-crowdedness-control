import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops in profiles: {len(stops)}")
hubs = [s for s in stops if s.get('is_major_hub')]
regular = [s for s in stops if not s.get('is_major_hub')]
print(f"Major Bus Stands (Black Dots): {len(hubs)}")
print(f"Regular Bus Stops (Blue Dots): {len(regular)}")

# Check coordinate precision: how many have only 2 or 3 decimal places (e.g. 28.52, 77.18)
rounded_stops = [s for s in stops if len(str(s['latitude']).split('.')[-1]) <= 3 or len(str(s['longitude']).split('.')[-1]) <= 3]
print(f"\nStops with coarse/rounded coordinates (<= 3 decimals, often floating off roads): {len(rounded_stops)}")
for r in rounded_stops[:25]:
    print(f"  COARSE: '{r['name']}' -> ({r['latitude']}, {r['longitude']}) - Hub: {r['is_major_hub']}")
