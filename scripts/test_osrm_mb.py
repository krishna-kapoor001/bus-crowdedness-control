import urllib.request
import json

pts = [
    (28.5217, 77.1827), # Mehrauli Terminal
    (28.5205, 77.2027), # Saket Metro Station
    (28.5180, 77.2320), # Khanpur Village
    (28.5126, 77.2485), # Hamdard Nagar
    (28.5030, 77.2880), # Lal Kuan
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
            print(f"SUCCESS: MB Road returned {len(geom)} street-snapped points!")
except Exception as e:
    print("Error:", e)
