import json

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

def interpolate_segment(p1, p2, num_steps=12):
    pts = []
    for step in range(num_steps):
        frac = step / float(num_steps)
        lat = round(p1[0] + (p2[0] - p1[0]) * frac, 6)
        lon = round(p1[1] + (p2[1] - p1[1]) * frac, 6)
        pts.append([lat, lon])
    return pts

for c in corridors:
    if c['id'] == 'route-623':
        # Vasant Kunj -> Munirka -> AIIMS -> Defence Colony -> Central Secretariat -> Kendriya Terminal
        pts = c['coordinates']
        # Extend from Defence Colony [28.574347, 77.228823] to Central Secretariat and Kendriya Terminal [28.6212, 77.2053]
        ext = [
            [28.574347, 77.228823],
            [28.5880, 77.2250], # Lodhi Road
            [28.6000, 77.2200], # Khan Market
            [28.6120, 77.2100], # Udyog Bhawan / Central Secretariat
            [28.6212, 77.2053]  # Kendriya Terminal
        ]
        dense_ext = []
        for i in range(len(ext)-1):
            dense_ext.extend(interpolate_segment(ext[i], ext[i+1], num_steps=15))
        dense_ext.append(ext[-1])
        c['coordinates'] = pts + dense_ext
        print("Extended route-623 to Kendriya Terminal!")

    elif c['id'] == 'route-894':
        # Extend backwards from Nehru Place [28.548608, 77.249221] to Okhla Phase 3 [28.5350, 77.2750]
        pts = c['coordinates']
        prefix = [
            [28.5350, 77.2750], # Okhla Phase 3 / Depot
            [28.5395, 77.2662], # Kalkaji Depot
            [28.5485, 77.2571], # Nehru Place Terminal
            [28.548608, 77.249221]
        ]
        dense_prefix = []
        for i in range(len(prefix)-1):
            dense_prefix.extend(interpolate_segment(prefix[i], prefix[i+1], num_steps=15))
        c['coordinates'] = dense_prefix + pts
        print("Extended route-894 to Okhla Depot!")

    elif c['id'] == 'route-548':
        # Extend backwards from Hamdard Nagar [28.511923, 77.249778] to Tughlaqabad Extension [28.5080, 77.2600]
        pts = c['coordinates']
        prefix = [
            [28.5080, 77.2600], # Tughlaqabad Extension
            [28.511923, 77.249778]
        ]
        dense_prefix = interpolate_segment(prefix[0], prefix[1], num_steps=15)
        c['coordinates'] = dense_prefix + pts
        print("Extended route-548 to Tughlaqabad Extension!")

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved all updated routes successfully!")
