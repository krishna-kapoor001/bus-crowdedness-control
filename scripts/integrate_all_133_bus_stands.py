import csv
import json
import re

print("Integrating all 133 Delhi Bus Stands into stop_profiles.json & stops_meta.json...", flush=True)

# 1. Load the 133 bus stands CSV
with open('delhi_bus_stands_coordinates.csv', mode='r', encoding='utf-8') as f:
    stands_133 = list(csv.DictReader(f))

print(f"Loaded {len(stands_133)} official bus stands from CSV.", flush=True)

# 2. Load current stop profiles
with open('data/processed/stop_profiles.json', mode='r', encoding='utf-8') as f:
    stops = json.load(f)

def clean_key(s):
    s = s.lower()
    s = re.sub(r'[\(\)\/\-\,\.]', ' ', s)
    tokens = [w for w in s.split() if w not in ('terminal', 'depot', 'isbt', 'stand', 'bus', 'station', 'crossing', 'xing', 't', 'gate', 'road', 'delhi', 'nct', 'dtc', 'cluster')]
    return "".join(tokens)

# Map existing stops by exact name, normalized name, and clean_key
stop_by_name = {s['name'].lower().strip(): s for s in stops}
stop_by_key = {}
for s in stops:
    k = clean_key(s['name'])
    if k and k not in stop_by_key:
        stop_by_key[k] = s

matched_count = 0
added_count = 0

for stand in stands_133:
    stand_name = stand['bus_stand_name'].strip()
    lat = float(stand['latitude'])
    lon = float(stand['longitude'])
    category = stand.get('category', 'Bus Stand')
    corridor = stand.get('corridor_locality', 'Delhi Major Transit Hub')

    # Try matching existing stop
    match = stop_by_name.get(stand_name.lower())
    if not match:
        k = clean_key(stand_name)
        if k in stop_by_key:
            match = stop_by_key[k]

    if match:
        # Update existing stop to be a major hub with ground-truth coordinates
        match['is_major_hub'] = True
        match['latitude'] = lat
        match['longitude'] = lon
        if not match.get('corridor') or match.get('corridor') == 'Delhi Transit Corridor':
            match['corridor'] = corridor
        matched_count += 1
    else:
        # Add new major hub
        new_hub = {
            "name": stand_name,
            "latitude": lat,
            "longitude": lon,
            "corridor": corridor,
            "monthly_boardings": 28000,
            "is_major_hub": True,
            "avg_fare_inr": 15.0,
            "dominant_payment": "Smart Card / Cash",
            "am_peak_ratio": 0.28,
            "pm_peak_ratio": 0.32,
            "offpeak_ratio": 0.40,
            "daily_footfall": 12000
        }
        stops.append(new_hub)
        stop_by_name[stand_name.lower()] = new_hub
        added_count += 1

print(f"Matched & updated {matched_count} existing stops. Added {added_count} new bus stands.", flush=True)

# Count total hubs now
hubs = [s for s in stops if s.get('is_major_hub')]
print(f"Total stops in database: {len(stops)}. Total Major Bus Stands (Black Dots): {len(hubs)}", flush=True)

# Save updated files
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

print("Saved data/processed/stop_profiles.json & data/stops_meta.json successfully!", flush=True)
