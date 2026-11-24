import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
print(f"Total major hubs: {len(hubs)}")

# Official Delhi Landmark / Terminal True Coordinates from OpenStreetMap & Delhi Transport:
GROUND_TRUTH_HUBS = {
    "ISBT Kashmere Gate": (28.6675, 77.2285),
    "Anand Vihar ISBT": (28.6468, 77.3160),
    "ISBT Sarai Kale Khan": (28.5886, 77.2530),
    "Dhaula Kuan": (28.5915, 77.1685),
    "AIIMS Transit Hub": (28.5685, 77.2115),
    "Nehru Place Terminal": (28.5485, 77.2520),
    "Azadpur Terminal": (28.7083, 77.1779),
    "Shivaji Stadium": (28.6300, 77.2140),
    "Central Secretariat": (28.6180, 77.2120),
    "Mehrauli Terminal": (28.5195, 77.1818),
    "Badarpur Border Terminal": (28.4984, 77.3045),
    "Karol Bagh Terminal": (28.6500, 77.1900),
    "Uttam Nagar Terminal": (28.6250, 77.0655),
    "Narela": (28.8520, 77.0940),
    "Mori Gate Terminal": (28.6650, 77.2250),
    "Ambedkar Stadium Terminal": (28.6380, 77.2420),
    "Anand Parvat Terminal": (28.6575, 77.1840),
    "Kalyanpuri Terminal": (28.6230, 77.3110),
    "Mayur Vihar Phase 1": (28.6040, 77.2960),
    "Mayur Vihar Phase 3 Terminal": (28.6120, 77.3320),
    "Rohini Sector 22 Terminal": (28.7250, 77.0680),
    "Dwarka Mor": (28.6190, 77.0330),
    "Dwarka Sector 10": (28.5810, 77.0570),
    "Najafgarh Terminal": (28.6150, 76.9770),
    "Shahdara Terminal": (28.6740, 77.2870),
    "Tilak Nagar": (28.6360, 77.0960),
    "Lajpat Nagar": (28.5700, 77.2400),
    "IIT Gate": (28.5450, 77.1950),
    "Munirka": (28.5580, 77.1740),
    "Saket": (28.5204, 77.2100)
}

print("\nComparing current coordinates with ground truth landmarks:")
for name, (gt_lat, gt_lon) in list(GROUND_TRUTH_HUBS.items())[:15]:
    # find in stops
    s_match = next((s for s in stops if name.lower() in s['name'].lower() or s['name'].lower() in name.lower()), None)
    if s_match:
        cur_lat, cur_lon = s_match['latitude'], s_match['longitude']
        from math import radians, sin, cos, atan2, sqrt
        dphi = radians(gt_lat - cur_lat)
        dlam = radians(gt_lon - cur_lon)
        a = sin(dphi/2)**2 + cos(radians(cur_lat))*cos(radians(gt_lat))*sin(dlam/2)**2
        dist_m = 6371000 * 2 * atan2(sqrt(a), sqrt(1-a))
        print(f"  {name:25s} -> Found '{s_match['name']}': dist = {dist_m:6.1f}m")
    else:
        print(f"  {name:25s} -> NOT FOUND in stop_profiles.json!")
