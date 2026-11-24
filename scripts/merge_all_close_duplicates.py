import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before cleanup: {len(stops)}")

# Define canonical merge mapping: drop_name -> keep_name
merge_map = {
    # 1. North Campus: Maurice Nagar II is right outside Ramjas College
    'Maurice Nagar II': 'Ramjas College',
    # 2. Typos & Exact duplicates
    'North Paint Nursing Home': 'North Point',
    'PS Tuglak Road': 'Prithviraj Road P.S.Tughlaq road',
    'Avantika Sec 2': 'Rohini Sec 1 Avantika',
    'Post Office': 'Gol Daak Khana',
    'ITO Ring Road': 'ITO',
    'Ladpur School': 'Ladpur Village',
    'Rajdhani Enclave Mahindra Park': 'Mahindra Park Road No 44',
    'A 3 Janak Puri': 'Mata Chandan Devi Hospital',
    'Janak Puri B 3': 'Bharti Public College',
    'SFS Quarter Gazipur': 'NHW 24 crossing',
    'Anandlok': 'Kamla Nehru College Niti Bag',
    'Air Force Officers Flats Dhaula Kuan': 'APS School Dhaula Kuan',
    'Saleemgarh Road': 'Geeta Colony Road Crossing',
    'Babarpur Extension': 'Mauj Pur',
    'Arjun Nagar': 'Radheypuri',
    'Crown Plaza': 'CRPF Camp Okhla Phase 1',
    'Burari Crossing': 'Burari Transport Authority',
    'Sujan Singh Park': 'Humayun Road Khan Mkt',
    'Siras Pur Crossing': 'Gurudwara',
    'Old Anaj Mandi': 'Primary School',
    'Corporation Bank': 'Issapur School',
    'Major Bhupinder Singh Marg': 'CRPF Camp Keshopur',
    'Fire Station Sec 8': 'Rohini East',
}

# Collect passenger volumes for dropped stops
add_boardings = {}
add_alightings = {}
for s in stops:
    if s['name'] in merge_map:
        target = merge_map[s['name']]
        add_boardings[target] = add_boardings.get(target, 0) + s.get('monthly_boardings', 0)
        add_alightings[target] = add_alightings.get(target, 0) + s.get('monthly_alightings', 0)

# Filter out the merged-away duplicate stops
cleaned_stops = []
for s in stops:
    if s['name'] in merge_map:
        continue
    # If this stop received volume from a merged stop, add it
    if s['name'] in add_boardings:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + add_boardings[s['name']]
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + add_alightings[s['name']]
    cleaned_stops.append(s)

print(f"Stops count after merging duplicates: {len(cleaned_stops)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(cleaned_stops, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
