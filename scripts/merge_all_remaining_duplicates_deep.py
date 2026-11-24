import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before merge: {len(stops)}")

# Drop -> Target merge map
merge_map = {
    # 1. 37.4m: New Friends Colony
    'Mata Mandir New Friends Colony': 'New Friends Colony',
    # 2. 37.7m: Keshav Puram
    'A 1 Keshav Puram': 'C 2 Keshav Puram',
    # 3. 39.6m: Sunder Vihar
    'Sunder Apartment': 'Sunder Vihar',
    # 4. 42.4m: Paharganj
    'Dispensary Paharganj': 'Police Station Paharganj',
    # 5. 42.6m: Okhla
    'CRPF Camp Okhla Phase 1': 'Okhla Depot Iv Cws Ii',
    # 6. 44.6m: DB Gupta Road
    'Thana DB Gupta Road': 'Prahlad Market',
    # 7. 45.2m: Nand Nagari
    'Sunder Nagri': 'Nand Nagari Terminal',
    # 8. 48.4m: Dwarka Sec 1
    'Dwarka Sec 1 Mahalaxmi Apartment': 'Dwarka Sec 1',
    # 9. 50.4m: Janakpuri B2
    'Desu Colony Janakpuri': 'Janakpuri B 2',
    # 10. 50.5m: Wazirpur / Shalimar Bagh
    'Shalimar Bagh BA Block': 'Wazir Pur Industrial Area Ashok Vihar Crossing',
    # 11. 53.5m: Mangolpuri
    'Mangolpuri School': 'B Block Mangol Puri',
    # 12. 53.9m: Centaur Hotel
    'Centaur Hotel Nangal Dairy': 'Centaur Hotel New Custom House',
    # 13. 54.3m: Delhi Gate / Ambedkar Stadium
    'Delhi Gate': 'Ambedkar Stadium Terminal',
    # 14. 56.8m: Tis Hazari / St Stephen's
    'Tees Hazari Animal Hospital Mori Gate': 'St Stephen Hospital',
    # 15. 57.9m: Jahangirpuri
    'Jahangirpuri B Block': 'Jahangirpuri GT Road',
    # 16. 63.5m: Rohini Sec 11/16
    'Rohini Sec 11 Agarwal Sabha': 'Rohini Sec 16',
    # 17. 65.6m: Jahangirpuri K Block
    'Jahangir Puri Outer Ring Road': 'Jahangirpuri K Block',
    # 18. 70.0m: Jhilmil Crossing
    'Dilshad Garden GT Road': 'Jhilmil Crossing',
    # 19. 72.8m: Bali Nagar / Ramesh Nagar
    'Basai Darapur Ramesh Nagar': 'Bali Nagar',
    # 20. 77.6m: Seelampur / Seelampur Market
    'Seelampur Market': 'Seelampur',
    # 21. 83.9m: Sheikh Sarai Colleges
    'Vocational College': 'Sheikh Sarai Phase Ii Shaheed Bhagat Singh College',
}

# Aggregate boardings and alightings
extra_boardings = {}
extra_alightings = {}
for s in stops:
    if s['name'] in merge_map:
        target = merge_map[s['name']]
        extra_boardings[target] = extra_boardings.get(target, 0) + s.get('monthly_boardings', 0)
        extra_alightings[target] = extra_alightings.get(target, 0) + s.get('monthly_alightings', 0)

clean_stops = []
for s in stops:
    if s['name'] in merge_map:
        continue
    if s['name'] in extra_boardings:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + extra_boardings[s['name']]
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + extra_alightings[s['name']]
    clean_stops.append(s)

print(f"Stops count after deep merge: {len(clean_stops)}")

with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(clean_stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(clean_stops, f, indent=2, ensure_ascii=False)

print("Saved cleanly to stop_profiles.json and stops_meta.json!")
