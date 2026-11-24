import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    profiles = json.load(f)

print(f"Initial stops: {len(profiles)}")

# 1. Panchsheel Club vs Panchsheel Enclave: separate them to their real distinct OSM locations!
# Panchsheel Club: 28.544483, 77.208732
# Panchsheel Enclave: 28.543098, 77.231353
for p in profiles:
    if p['name'] == 'Panchsheel Club':
        p['latitude'] = 28.544483
        p['longitude'] = 77.208732
    elif p['name'] == 'Panchsheel Enclave':
        p['latitude'] = 28.543098
        p['longitude'] = 77.231353

# 2. Shastri Park Depot vs Shastri Park Pusta Road:
# Shastri Park DMRC Depot is at 28.673777, 77.241395
# Shastri Park Pusta Road remains at 28.673141, 77.255794
for p in profiles:
    if p['name'] == 'Shastri Park Depot':
        p['latitude'] = 28.673777
        p['longitude'] = 77.241395

# 3. Gazipur Depot vs TELCO Gazipur:
# Merge TELCO Gazipur into Gazipur Depot so there is only ONE clean dot at Gazipur Depot
telco_boardings = 0
telco_alightings = 0
filtered_profiles = []
for p in profiles:
    if p['name'] == 'TELCO Gazipur':
        telco_boardings = p.get('monthly_boardings', 0)
        telco_alightings = p.get('monthly_alightings', 0)
        continue
    filtered_profiles.append(p)

for p in filtered_profiles:
    if p['name'] == 'Gazipur Depot':
        p['monthly_boardings'] = p.get('monthly_boardings', 0) + telco_boardings
        p['monthly_alightings'] = p.get('monthly_alightings', 0) + telco_alightings

print(f"Updated stops count: {len(filtered_profiles)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_profiles, f, indent=2)

# Also update data/stops_meta.json
with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_profiles, f, indent=2)

print("Saved to stop_profiles.json and stops_meta.json!")
