import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Initial stops: {len(stops)}")

merge_map = {
    # 1. Britannia Chowk (100.5m)
    'Shakurpur JJ Colony Britannia': 'Britannia',
    # 2. Subroto Park (103.6m)
    'Air Force HQ Subroto Park': 'Subroto Park',
    # 3. Janakpuri District Centre (144.0m)
    'District Centre Nazafgarh Road': 'Janakpuri District Centre',
    # 4. East Krishna Nagar (153.2m)
    'Krishna Nagar A Block': 'East Krishna Nagar',
    # 5. Metcalf House (170.0m)
    'Raksha Vigyan Kendra Metcalf House': 'Metcalfe House',
    # 6. Raja Garden (183.7m)
    'Raja Garden': 'Raja Garden Terminal',
    # 7. Andheria Mor (186.9m)
    'Andheria Bagh More': 'Andheria More',
    # 8. Rithala (187.1m)
    'Rithala Village': 'Rithala Crossing',
    # 9. Ashram Chowk (191.9m)
    'Ashram Ring Road': 'Ashram Chowk',
    # 10. Shakti Nagar (194.1m)
    'Roop Nagar Shakti Nagar': 'Shakti Nagar',
    # 11. Rajendra Nagar (195.5m)
    'R Block Rajendra Nagar': 'New Rajender Nagar',
    # 12. Inderpuri (196.4m)
    'Inder Puri JJ Colony': 'Inder Puri',
}

extra_b = {}
extra_a = {}
for s in stops:
    if s['name'] in merge_map:
        target = merge_map[s['name']]
        extra_b[target] = extra_b.get(target, 0) + s.get('monthly_boardings', 0)
        extra_a[target] = extra_a.get(target, 0) + s.get('monthly_alightings', 0)

filtered = []
for s in stops:
    if s['name'] in merge_map:
        continue
    if s['name'] in extra_b:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + extra_b[s['name']]
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + extra_a[s['name']]
    filtered.append(s)

print(f"Stops count after merging 12 semantic duplicates: {len(filtered)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
