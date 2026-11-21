import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

replace_map = {
    'raj ghat': 'ITO Ring Road',
    'hauz khas terminal': 'Hauz Rani',
    'mukarba chowk crossing': 'Jahangirpuri',
    'singhu border gt road': 'Alipur Village',
    'qutab minar': 'Qutub Minar Metro Sation',
    'delhi cantt railway station': 'Dhaula Kuan',
    'guru ravi das ashram / tughlaqabad extension': 'Tughlaqabad Village'
}

for c in corridors:
    new_stops = []
    for s in c.get('stops', []):
        low = s.lower().strip()
        if low in replace_map:
            new_stops.append(replace_map[low])
        else:
            new_stops.append(s)
    c['stops'] = new_stops

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Mapped case-insensitively!")
