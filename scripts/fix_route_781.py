import json
import urllib.request
import time

def get_osrm(c1, c2):
    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiAudit/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok':
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print("OSRM error:", e)
    return []

# route-781 stops:
# 1. New Delhi Railway Station (28.6420, 77.2210)
# 2. Shivaji Stadium (28.6310, 77.2158)
# 3. Dhaula Kuan (28.60005, 77.162017)
# 4. airport_poly (from Dhaula Kuan down to Kapashera Border)

corridors_file = 'data/processed/corridors_routed.json'
with open(corridors_file, 'r', encoding='utf-8') as f:
    corridors = json.load(f)

airport_poly = [c for c in corridors if c['id'] == 'corridor-airport'][0]['coordinates']

ndls = (28.6420, 77.2210)
shivaji = (28.6310, 77.2158)
dhaula = (28.60005, 77.162017)

seg1 = get_osrm(ndls, shivaji)
time.sleep(0.3)
seg2 = get_osrm(shivaji, dhaula)

full_781 = []
if seg1: full_781.extend(seg1)
if seg2:
    if full_781 and seg2 and full_781[-1] == seg2[0]:
        full_781.extend(seg2[1:])
    else:
        full_781.extend(seg2)
if airport_poly:
    if full_781 and airport_poly and full_781[-1] == airport_poly[0]:
        full_781.extend(airport_poly[1:])
    else:
        full_781.extend(airport_poly)

for c in corridors:
    if c['id'] == 'route-781':
        c['coordinates'] = full_781
        print(f"Updated route-781 polyline: {len(full_781)} points.")

with open(corridors_file, 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved cleanly!")
