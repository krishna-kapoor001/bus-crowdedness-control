import json

corridors = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))
print(f"Total corridors/routes: {len(corridors)}")
for c in corridors:
    pts = c.get('coordinates', [])
    stops = c.get('stops', [])
    print(f"{c['id']:<24}: {len(pts):>4} pts | {len(stops):>2} stops | {c['name']}")
