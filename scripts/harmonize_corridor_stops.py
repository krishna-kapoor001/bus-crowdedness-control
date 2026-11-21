import json

with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corridors = json.load(f)

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

stop_names = {s['name'].lower().strip(): s['name'] for s in stops}

# Map of corridor stop variations to exact profile names
NAME_ALIGNMENT = {
    'aiims': 'Aiims',
    'anand vihar isbt': 'Anand Vihar Isbt',
    'hazrat nizamuddin': 'Nizamuddin Railway Station',
    'nizamuddin': 'Nizamuddin Railway Station',
    'model town': 'Model Town Ii',
    'rajghat': 'Dtc Rajghat Depot',
    'alipur': 'Alipur Gt Road',
    'okhla industrial area': 'Okhla Depot Iv Cws Ii',
    'singhu border': 'Narela',
    'mukarba chowk': 'Azadpur',
    'tuglakabad extension': 'Hamdard Nagar / Sangam Vihar',
    'subhash nagar': 'Subhash Nagar Crossing / More',
    'tilak nagar': 'Tilak Nagar Crossing'
}

changes = 0
for c in corridors:
    new_stops = []
    for s in c.get('stops', []):
        s_low = s.lower().strip()
        if s_low in stop_names:
            new_stops.append(stop_names[s_low])
        elif s_low in NAME_ALIGNMENT:
            aligned_name = NAME_ALIGNMENT[s_low]
            new_stops.append(aligned_name)
            changes += 1
            print(f"Aligned in corridor '{c['id']}': '{s}' -> '{aligned_name}'")
        else:
            # find closest
            matches = [name for low, name in stop_names.items() if s_low in low or low in s_low]
            if matches:
                new_stops.append(matches[0])
                changes += 1
                print(f"Matched in corridor '{c['id']}': '{s}' -> '{matches[0]}'")
            else:
                new_stops.append(s)
                print(f"UNMATCHED in corridor '{c['id']}': '{s}'")
    c['stops'] = new_stops

print(f"Total corridor stop alignments: {changes}")

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

with open('data/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved updated corridors_routed.json!")
