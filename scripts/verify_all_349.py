import json
from collections import defaultdict

stops = json.load(open('data/processed/stop_profiles.json', encoding='utf-8'))

by_corridor = defaultdict(list)
for s in stops:
    by_corridor[s.get('corridor', 'Unknown')].append(s)

print(f"Total Corridors/Zones: {len(by_corridor)}")
for corr, slist in sorted(by_corridor.items()):
    print(f"\n--- {corr} ({len(slist)} stops) ---")
    for s in slist[:6]:
        print(f"  {s['name']} -> ({s['latitude']}, {s['longitude']}) [boardings: {s.get('monthly_boardings', 0)}]")
