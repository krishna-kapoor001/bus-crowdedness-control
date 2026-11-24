import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before merge: {len(stops)}")

merge_map = {
    # 1. Jhandewalan cluster (164m, 195m)
    'Rani Jhansi Road Jhande Walan': 'Jhandewalan',
    # 2. Nehru Place Paras Cinema / Apartments (269m, 273m)
    'Nehru Place Apartments': 'Nehru Place Crossing Paras Cinema',
    # 3. Mayapuri Crossing / Depot (249m)
    'Maya Puri Crossing Ring Road': 'Mayapuri Depot',
    # 4. Keshav Puram redundant blocks (161m, 182m)
    'B3 Keshav Puram': 'B 4 Keshav Puram',
    'C 8 Keshav Puram': 'B 4 Keshav Puram',
    # 5. Khayala More Subhash Nagar / Raghubir Nagar (86.7m)
    'Raghubir Nagar F Block': 'Khayala More Subhash Nagar Crossing',
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

print(f"Stops count after merging deep clusters: {len(filtered)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
