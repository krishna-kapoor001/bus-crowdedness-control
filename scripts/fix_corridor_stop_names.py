import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# Name normalization map to match exact stop names in stop_profiles.json
name_map = {
    'rajghat': 'Raj Ghat',
    'hauz khas': 'Hauz Khas Terminal',
    'okhla': 'Okhla Phase 3',
    'model town': 'Model Town Ii',
    'mukarba chowk': 'Mukarba Chowk Crossing',
    'alipur': 'Alipur Village',
    'singhu border': 'Singhu Border GT Road',
    'safdarjung tomb': 'Safdarjung Hospital',
    'qutub minar': 'Qutab Minar',
    'hazrat nizamuddin': 'Nizamuddin Railway Station',
    'central secretariat': 'Kendriya Terminal / Gurudwara Rakab Gunj',
    'karol bagh': 'Karol Bagh Metro Station',
    'delhi cantt': 'Delhi Cantt Railway Station',
    'uttam nagar': 'Uttam Nagar Terminal',
    'adhchini': 'Adhchini Village',
    'nand nagri': 'Nand Nagri Depot',
    'okhla industrial area': 'Okhla Phase 3',
    'naraina': 'Naraina Vihar',
    'tuglakabad extension': 'Guru Ravi Das Ashram / Tughlaqabad Extension'
}

for c in corridors:
    new_stops = []
    for s in c.get('stops', []):
        low = s.lower().strip()
        if low in name_map:
            new_stops.append(name_map[low])
        else:
            new_stops.append(s)
    c['stops'] = new_stops

# Save back to corridors_routed.json
with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Updated corridors_routed.json stop names!")
