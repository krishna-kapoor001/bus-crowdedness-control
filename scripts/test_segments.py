import urllib.request
import json

def get_osrm(c1, c2):
    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiAudit/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok':
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        pass
    return []

stops = [
    ("Dhaula Kuan", (28.60005, 77.162017)),
    ("Satya Niketan", (28.587833, 77.170333)),
    ("Mahipal Pur Crossing", (28.546733, 77.125)),
    ("Mahipal Pur", (28.5468, 77.1237)),
    ("Shiv Murti", (28.536033, 77.1119)),
    ("Rajokri Flyover", (28.5140, 77.0950)),
    ("Kapashera Border", (28.5217, 77.082117))
]

for i in range(len(stops)-1):
    n1, c1 = stops[i]
    n2, c2 = stops[i+1]
    seg = get_osrm(c1, c2)
    min_lon = min(p[1] for p in seg) if seg else 0
    print(f"{n1} -> {n2}: {len(seg)} pts | min lon: {min_lon:.5f}")
