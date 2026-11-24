import json
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

hubs = [s for s in stops if s.get('is_major_hub')]
print(f"Total Major Hubs (Black Dots): {len(hubs)}")

for idx, h in enumerate(hubs, 1):
    print(f"{idx:2d}. '{h['name']}' at ({h['latitude']}, {h['longitude']}) - Boardings: {h.get('monthly_boardings', 0)}")
