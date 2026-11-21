import json

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    stops = json.load(f)

for s in stops:
    if any(w in s['name'].lower() for w in ['crpf', 'crown', 'prehlad', 'samalkha', 'kali mata', 'sant nagar', 'tilak pul']):
        print(s)

with open('data/processed/corridors_routed.json', encoding='utf-8') as f:
    corrs = json.load(f)

for c in corrs:
    for s in c.get('stops', []):
        if any(w in s.lower() for w in ['crpf', 'crown', 'prehlad', 'samalkha', 'kali mata', 'sant nagar', 'tilak pul']):
            print(f"Corridor '{c['name']}': stop '{s}'")
