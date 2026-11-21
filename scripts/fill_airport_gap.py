import json
import urllib.request
import time

def get_osrm_retry(c1, c2, max_retries=5):
    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=full&geometries=geojson"
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiFill/1.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())
                if data.get('code') == 'Ok':
                    return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            time.sleep(1.5)
    return None

c1 = (28.587866, 77.170399) # Satya Niketan
c2 = (28.546657, 77.124954) # Mahipalpur Crossing

print("Fetching missing NH-48 segment between Satya Niketan & Mahipalpur Crossing...")
seg = get_osrm_retry(c1, c2)
if not seg:
    print("Failed to get segment from OSRM, using dense interpolation along NH-48...")
    # Key intermediate points along NH-48 (Delhi Gurgaon Expressway):
    # Satya Niketan -> Moti Bagh Flyover -> Rao Tula Ram Marg Flyover -> Shankar Vihar Flyover -> Mahipalpur Flyover
    nh48_via = [
        [28.587866, 77.170399],
        [28.581000, 77.166000],
        [28.572000, 77.158000],
        [28.562000, 77.148000],
        [28.553000, 77.136000],
        [28.546657, 77.124954]
    ]
    seg = nh48_via
else:
    print(f"Successfully retrieved segment: {len(seg)} points!")

corridors_file = 'data/processed/corridors_routed.json'
with open(corridors_file, 'r', encoding='utf-8') as f:
    corridors = json.load(f)

for c in corridors:
    if c['id'] == 'corridor-airport':
        pts = c['coordinates']
        # Find index 67 where gap is
        pts_new = pts[:68] + seg[1:-1] + pts[68:]
        c['coordinates'] = pts_new
        print(f"New total points for corridor-airport: {len(pts_new)}")

with open(corridors_file, 'w', encoding='utf-8') as f:
    json.dump(corridors, f, indent=2, ensure_ascii=False)

print("Saved updated corridor-airport polyline!")
