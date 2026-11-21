import urllib.request
import json

pts = [
    (28.6743, 77.2871), # Shahdara
    (28.6729, 77.2699), # Seelampur
    (28.6313, 77.2789), # Laxmi Nagar
    (28.6483, 77.3178), # Anand Vihar ISBT
    (28.6041, 77.2944)  # Mayur Vihar Phase 1
]

coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in pts)
url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        if data.get('code') == 'Ok':
            geom = [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
            print(f"SUCCESS: Trans-Yamuna returned {len(geom)} street-snapped points!")
except Exception as e:
    print("Error:", e)
