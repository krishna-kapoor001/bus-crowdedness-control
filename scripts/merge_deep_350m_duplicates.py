import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before merging 19 duplicates: {len(stops)}")

merge_map = {
    # 1. Kamla Nehru College typo (225m)
    'Kalma Nehru College': 'Kamla Nehru College Niti Bag',
    # 2. Humayun Road (221m)
    'Humayun Road': 'Humayun Road Khan Mkt',
    # 3. Ashram (296m)
    'Ashram': 'Ashram Chowk',
    # 4. Moti Nagar (209m)
    'Moti Nagar Market': 'Moti Nagar',
    # 5. Geetanjali Enclave (213m)
    'PNB Geetanjali': 'Geetanjali Enclave',
    # 6. Shakarpur (308m)
    'Shakarpur': 'Shakarpur Crossing',
    # 7. Sarai Rohilla (315m)
    'Sarai Rohilla Flyover': 'Sarai Rohila',
    # 8. Kalyanpuri (215m)
    'Kalyan Puri crossing': 'Kalyan Puri Terminal',
    # 9. Rajendra Place (274m)
    'Rajendra Place Karol Bagh Telephone Exchange': 'Rajendra Place',
    # 10. Lodhi Colony (275m)
    '18 Block Lodhi Colony': 'Lodhi Colony',
    # 11. Sunder Nagar (289m)
    'Golf Club Sunder Nagar': 'Sunder Nagar',
    # 12. Shadipur (289m)
    'Shadipur DTC Colony': 'Shadipur Depot',
    # 13. Panchkuian Road (298m)
    'Panchkuian Road Banwai Lal Hospital': 'Panchkuian Road',
    # 14. Hasanpur Depot / Village (299m)
    'Hassanpur Village': 'Hasanpur Depot',
    # 15. Shahdara (300m)
    'Shahdara Railway Bridge': 'Shahdara Terminal',
    # 16. Ramprastha (245m)
    'Ram Prastha Temple': 'Ram Prastha Crossing',
    # 17. Kakrola (243m)
    'Kakrola Bridge': 'Kakrola crossing',
    # 18. Munirka (216m)
    'Munirka Family Planning': 'Munirka Village',
    # 19. Najafgarh (333m)
    'Jharoda Crossing Nazafgarh Terminal': 'Najafgarh Terminal',
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

print(f"Stops count after merging 19 duplicates: {len(filtered)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
