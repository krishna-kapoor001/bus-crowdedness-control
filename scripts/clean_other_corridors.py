import json
import math

with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

stops_map = {s['name'].lower().strip(): (s['latitude'], s['longitude']) for s in stops}

def dist_m(p1, p2):
    return math.hypot(p1[0]-p2[0], p1[1]-p2[1]) * 111000

def interpolate_segment(p1, p2, num_steps=12):
    pts = []
    for step in range(num_steps):
        frac = step / float(num_steps)
        lat = round(p1[0] + (p2[0] - p1[0]) * frac, 6)
        lon = round(p1[1] + (p2[1] - p1[1]) * frac, 6)
        pts.append([lat, lon])
    return pts

# 1. Outer Ring Road: Munirka -> IIT Gate -> Chirag Delhi -> Nehru Place -> Kalkaji -> Okhla
for c in corridors:
    if c['id'] == 'corridor-outer-ring':
        c['stops'] = [
            "Munirka Village",
            "Iit Gate",
            "Chirag Delhi",
            "Nehru Place Terminal",
            "Kalkaji Depot",
            "Okhla Industrial Area"
        ]
        # Precise Outer Ring Road centerline from West to East:
        outer_centerline = [
            [28.55800, 77.17200], # Munirka
            [28.55100, 77.18500], # Ber Sarai / JNU
            [28.54585, 77.20250], # IIT Gate Flyover
            [28.54350, 77.21500], # Panchsheel Enclave
            [28.54700, 77.22500], # Chirag Delhi Flyover
            [28.54800, 77.24000], # Greater Kailash Enclave
            [28.54851, 77.25716], # Nehru Place Terminal
            [28.53947, 77.26623], # Kalkaji Depot
            [28.53500, 77.27500]  # Okhla Industrial Area
        ]
        dense = []
        for i in range(len(outer_centerline) - 1):
            dense.extend(interpolate_segment(outer_centerline[i], outer_centerline[i+1], num_steps=18))
        dense.append(outer_centerline[-1])
        c['coordinates'] = dense
        print("Cleaned corridor-outer-ring!")

    elif c['id'] == 'corridor-transyamuna':
        # Trans-Yamuna East: Shahdara -> Seelampur -> Laxmi Nagar -> Anand Vihar ISBT -> Mayur Vihar Phase 1
        c['stops'] = [
            "Shahdara Terminal",
            "Seelampur",
            "Laxmi Nagar",
            "Anand Vihar ISBT",
            "Mayur Vihar Phase 1"
        ]
        # Clean sequential road path:
        # Shahdara (North) -> Seelampur -> Shastri Park -> Geeta Colony Flyover -> Laxmi Nagar (Vikas Marg) -> Anand Vihar (Road 56) -> Mayur Vihar (Noida Link Road)
        ty_centerline = [
            [28.67429, 77.28712], # Shahdara Terminal
            [28.67292, 77.26995], # Seelampur
            [28.65500, 77.26500], # Shastri Park
            [28.63800, 77.27200], # Geeta Colony
            [28.63130, 77.27890], # Laxmi Nagar
            [28.63500, 77.30000], # Karkardooma / Vikas Marg Ext
            [28.64830, 77.31780], # Anand Vihar ISBT
            [28.63000, 77.31000], # Ghazipur / Road 56
            [28.61500, 77.30200], # Mayur Vihar Pocket 1
            [28.60410, 77.29440]  # Mayur Vihar Phase 1 Metro
        ]
        dense = []
        for i in range(len(ty_centerline) - 1):
            dense.extend(interpolate_segment(ty_centerline[i], ty_centerline[i+1], num_steps=18))
        dense.append(ty_centerline[-1])
        c['coordinates'] = dense
        print("Cleaned corridor-transyamuna!")

with open('data/processed/corridors_routed.json', 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved clean corridors successfully!")
