import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

def interpolate_pts(anchors, pts_per_km=18):
    dense = []
    import math
    for i in range(len(anchors) - 1):
        p1 = anchors[i]
        p2 = anchors[i+1]
        dist_km = math.hypot(p1[0]-p2[0], p1[1]-p2[1]) * 111.0
        steps = max(4, int(dist_km * pts_per_km))
        for s in range(steps):
            frac = s / float(steps)
            lat = round(p1[0] + (p2[0] - p1[0]) * frac, 6)
            lon = round(p1[1] + (p2[1] - p1[1]) * frac, 6)
            dense.append([lat, lon])
    dense.append([round(anchors[-1][0], 6), round(anchors[-1][1], 6)])
    return dense

# Route 181 proper sequential order:
# Nizamuddin -> ITO -> Kashmere Gate -> Civil Lines -> Azadpur Terminal -> Model Town -> Jahangirpuri
anchors_181 = [
    [28.5880, 77.2530], # Hazrat Nizamuddin
    [28.6290, 77.2490], # ITO Ring Road
    [28.6500, 77.2450], # Rajghat
    [28.6675, 77.2285], # Kashmere Gate
    [28.6950, 77.2150], # Civil Lines
    [28.7072, 77.1783], # Azadpur Terminal
    [28.7180, 77.1750], # Model Town
    [28.7255, 77.1635]  # Jahangirpuri
]

for c in corridors:
    if c['id'] == 'route-181':
        c['stops'] = [
            "Hazrat Nizamuddin", "ITO Ring Road", "Kashmere Gate",
            "Azadpur Terminal", "Model Town", "Jahangirpuri"
        ]
        c['coordinates'] = interpolate_pts(anchors_181)
        print("Fixed route-181 anchors cleanly!")

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved cleanly!")
