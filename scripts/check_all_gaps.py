import json

data = json.load(open('data/processed/corridors_routed.json', encoding='utf-8'))
print(f"Checking gaps across all {len(data)} corridors...")
for c in data:
    pts = c['coordinates']
    max_gap = 0
    for i in range(len(pts)-1):
        gap = ((pts[i][0]-pts[i+1][0])**2 + (pts[i][1]-pts[i+1][1])**2)**0.5
        if gap > max_gap:
            max_gap = gap
    km = max_gap * 111
    if km > 1.0:
        print(f"Warning: {c['id']} max gap = {km:.2f} km")
print("Gap audit complete.")
