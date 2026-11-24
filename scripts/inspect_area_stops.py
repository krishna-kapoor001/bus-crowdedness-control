import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print('Sample stops in North Campus:')
for s in stops:
    if any(k in s['name'].lower() for k in ['hansraj', 'kirodi', 'kirori', 'hindu', 'stephen', 'ramjas', 'malka ganj', 'kamla nagar', 'roop nagar', 'maurice nagar']):
        print(f"  {s['name']}: ({s['latitude']}, {s['longitude']}) - Hub: {s['is_major_hub']}")
