import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corrs = json.load(f)

# Phantoms to check
phantoms = [
    'Janak Puri B 1 Terminal', 'Jai Mata Market Tri Nagar Terminal', 'Dwarka Mor Bus Stand',
    'Prem Nagar', 'Samaypur School', 'Jhilmil Crossing', 'Govind Puri', 'Shaheen Bagh Thokar No 5',
    'Avtar Enclave', 'IOC Dwarka Road', 'Shivani Apartments Kunj Vihar Sector 12 Dwarka',
    'Lokesh Cinema Nangloi JJ Colony', 'Dwarka Sec 19 20 Crossing', 'Tikri Hospital',
    'Nangli Dairy', 'Lajpat Nagar', 'Hans Apartment', 'INA Colony', 'Nawada Gaon',
    'Aero City', 'Jor Bagh', 'KarKarDooma Court', 'Gokul Puri', 'Chand Nagar',
    'Mundka Village', 'Nangloi', 'Rajdhani Park', 'Tikri Border',
    'Dwarka Sec 16C GGS IP University', 'Palam Gaon', 'Surajmal Stadium', 'Udyog Nagar'
]

print("Checking which phantoms appear in corridors_routed.json:")
for c in corrs:
    c_stops = [s.lower() for s in c.get('stops', [])]
    matched = [p for p in phantoms if p.lower() in c_stops]
    if matched:
        print(f"Corridor '{c['id']}' ({c['name']}) has: {matched}")
