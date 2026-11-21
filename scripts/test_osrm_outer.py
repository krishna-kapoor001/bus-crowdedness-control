import urllib.request
import json

pts = [
    (28.5580, 77.1720), # Munirka
    (28.5458, 77.2025), # IIT Gate Flyover
    (28.5470, 77.2250), # Chirag Delhi
    (28.5485, 77.2571), # Nehru Place Terminal
    (28.5395, 77.2662), # Kalkaji Depot
    (28.5350, 77.2750)  # Okhla Industrial Area
]

coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in pts)
url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        if data.get('code') == 'Ok':
            geom = [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
            print(f"SUCCESS: Outer Ring Road returned {len(geom)} street-snapped points!")
except Exception as e:
    print("Error:", e)
