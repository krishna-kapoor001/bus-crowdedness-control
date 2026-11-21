import urllib.request
import json

pts = [
    (28.6373, 77.2412), # Delhi Gate
    (28.6180, 77.2440), # Pragati Maidan
    (28.5880, 77.2530), # Nizamuddin
    (28.5714, 77.2592), # Ashram
    (28.5350, 77.2800), # Apollo Hospital
    (28.4984, 77.3045)  # Badarpur Border
]

coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in pts)
url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        if data.get('code') == 'Ok':
            geom = [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
            print(f"SUCCESS: Mathura Road returned {len(geom)} street-snapped points!")
except Exception as e:
    print("Error:", e)
