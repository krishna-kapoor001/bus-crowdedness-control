import json
import urllib.request
import time

def get_osrm(c1, c2):
    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiAudit/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok':
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print("Error fetching OSRM:", e)
    return []

# Precise NH-48 waypoints:
# Dhaula Kuan -> Satya Niketan -> Mahipalpur Crossing -> Mahipalpur -> Shiv Murti (Southbound) -> Rajokri Flyover -> Kapashera Border
airport_anchors = [
    (28.60005, 77.162017), # Dhaula Kuan
    (28.587833, 77.170333), # Satya Niketan
    (28.546733, 77.125000), # Mahipal Pur Crossing
    (28.546800, 77.123700), # Mahipal Pur
    (28.535800, 77.112200), # Shiv Murti (Southbound NH-48)
    (28.514000, 77.095000), # Rajokri Flyover
    (28.521700, 77.082117)  # Kapashera Border
]

print("Routing Airport Expressway Corridor directly along NH-48...")
airport_poly = []
for i in range(len(airport_anchors)-1):
    seg = get_osrm(airport_anchors[i], airport_anchors[i+1])
    if seg:
        if airport_poly and seg and airport_poly[-1] == seg[0]:
            airport_poly.extend(seg[1:])
        else:
            airport_poly.extend(seg)
    time.sleep(0.3)

print(f"Airport Corridor polyline: {len(airport_poly)} points.")
min_lon = min(p[1] for p in airport_poly)
max_lon = max(p[1] for p in airport_poly)
print(f"Lon range: {min_lon:.5f} to {max_lon:.5f}")

# Update corridors_routed.json
corridors_file = 'data/processed/corridors_routed.json'
with open(corridors_file, 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    if c['id'] == 'corridor-airport':
        c['coordinates'] = airport_poly
        print("Updated corridor-airport polyline in corridors_routed.json!")
    elif c['id'] == 'route-781':
        # New Delhi Railway Station -> Shivaji Stadium -> Dhaula Kuan -> Mahipalpur -> Kapashera Border
        # Let's check route-781 coordinates
        # If it has the old detour, let's keep Dhaula Kuan to Kapashera as the new clean segment!
        poly = c['coordinates']
        # Find index near Dhaula Kuan
        dhaula_idx = -1
        for idx, pt in enumerate(poly):
            if abs(pt[0] - 28.60005) < 0.005 and abs(pt[1] - 77.1620) < 0.005:
                dhaula_idx = idx
                break
        if dhaula_idx != -1:
            c['coordinates'] = poly[:dhaula_idx] + airport_poly
            print(f"Updated route-781 with clean NH-48 polyline ({len(c['coordinates'])} points)!")

with open(corridors_file, 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved data/processed/corridors_routed.json successfully!")
