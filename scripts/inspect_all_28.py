import json

data = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))
print(f"Total entries: {len(data)}")
for i, c in enumerate(data):
    print(f"[{i+1}] {c['id']} ({c.get('type')}) - {c['name']}")
    print(f"    Stops ({len(c.get('stops', []))}): {c.get('stops')}")
    pts = c.get('coordinates', [])
    print(f"    Points: {len(pts)} | Start: {pts[0] if pts else None} | End: {pts[-1] if pts else None}")
