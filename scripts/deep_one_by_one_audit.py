import json, math, os, sqlite3
from collections import defaultdict

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

# Load stops
with open(os.path.join(DATA_DIR, 'stops_meta.json'), 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops to audit: {len(stops)}")

# 1. Check duplicate pairs < 60m
clusters = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i + 1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 60:
            clusters.append((d, s1['name'], s2['name'], s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude']))

clusters.sort(key=lambda x: x[0])
print(f"\n[AUDIT 1] Clustered / Duplicate dots (< 60m): {len(clusters)}")
for d, n1, n2, lat1, lon1, lat2, lon2 in clusters[:20]:
    print(f"  {d:.1f}m: '{n1}' vs '{n2}'")

# 2. Check Delhi NCT boundaries
outside_delhi = []
for s in stops:
    lat, lon = s['latitude'], s['longitude']
    if not (28.40 <= lat <= 28.88 and 76.83 <= lon <= 77.35):
        outside_delhi.append(s)

print(f"\n[AUDIT 2] Stops outside Delhi NCT boundaries: {len(outside_delhi)}")
for s in outside_delhi:
    print(f"  {s['name']} at ({s['latitude']}, {s['longitude']})")

# 3. Check expressway proximity & high speed zones
# Expressways to check:
# - Delhi-Meerut Expressway: Sarai Kale Khan to Ghazipur
# - Barapullah: Sarai Kale Khan to INA
# - DND Flyway: Maharani Bagh across river
# - NH-48: Dhaula Kuan to Rajokri
expressway_boxes = [
    ("Delhi-Meerut Expressway", 28.615, 28.635, 77.275, 77.335),
    ("Barapullah Elevated", 28.580, 28.590, 77.225, 77.255),
    ("DND Flyway Bridge", 28.572, 28.582, 77.270, 77.310),
    ("NH-48 Central Line", 28.530, 28.560, 77.095, 77.135)
]

exp_stops = []
for s in stops:
    for name, min_lat, max_lat, min_lon, max_lon in expressway_boxes:
        if min_lat <= s['latitude'] <= max_lat and min_lon <= s['longitude'] <= max_lon:
            exp_stops.append((name, s))

print(f"\n[AUDIT 3] Stops in expressway corridors: {len(exp_stops)}")
for exp_name, s in exp_stops[:15]:
    print(f"  [{exp_name}] {s['name']}: ({s['latitude']}, {s['longitude']})")
