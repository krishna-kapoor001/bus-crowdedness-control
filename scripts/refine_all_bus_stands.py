import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Identify non-hub stops that were mistakenly marked as is_major_hub: True
demote_to_regular = [
    'Munirka Village',                        # Roadside stop on Outer Ring Road (Vasant Vihar Depot is the hub)
    'Jharoda Crossing Nazafgarh Terminal',    # Crossing stop (Najafgarh Terminal is the hub)
    'Begumpur',                               # Village stop in Rohini (Rohini Sec 22 Terminal / Depot 2 is the hub)
    'Okhla Village',                          # Local street stop (Okhla Depot is the hub)
    'Mayur Vihar Phase 1',                    # Local street stop (Mayur Vihar Phase 3 Terminal is the hub)
    'Tilak Nagar',                            # Roadside metro/market stop
    'Lodhi Colony',                           # Roadside market stop (JLN Stadium Terminal is the hub)
]

# Rename abbreviations for crystal clarity
rename_map = {
    'SNPD': 'Sriniwaspuri DTC Depot (SNPD)',
    'Ordinance Depot': 'Ordnance Depot (Shakurbasti)',
    'Supply Depot': 'Supply Depot (Delhi Cantt)',
    'BBM Cluster Depot': 'BBM DTC Depot (Kingsway Camp)',
    'DTC Bus Depot Yamuna Vihar': 'Yamuna Vihar DTC Depot',
}

demoted_count = 0
renamed_count = 0

for s in stops:
    if s['name'] in demote_to_regular:
        s['is_major_hub'] = False
        demoted_count += 1
    if s['name'] in rename_map:
        s['name'] = rename_map[s['name']]
        renamed_count += 1

hubs_remaining = [s for s in stops if s.get('is_major_hub', False)]
print(f"Demoted {demoted_count} non-hub stops to regular street stops.")
print(f"Renamed {renamed_count} hubs with professional clear names.")
print(f"Total authentic Major Bus Stands & Terminals: {len(hubs_remaining)}")

# Save cleanly
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(stops, f, indent=2, ensure_ascii=False)

print("Saved updated stops to stop_profiles.json and stops_meta.json!")
