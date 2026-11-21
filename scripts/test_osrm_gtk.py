import urllib.request
import json

# GT Karnal Road centerline points:
# Azadpur Terminal -> Model Town -> Jahangirpuri -> Mukarba Chowk -> Alipur -> Singhu Border
pts = [
    (28.7072, 77.1783), # Azadpur
    (28.7180, 77.1750), # Model Town
    (28.7255, 77.1635), # Jahangirpuri
    (28.7520, 77.1550), # Mukarba Chowk
    (28.7981, 77.1352), # Alipur
    (28.8250, 77.1200)  # Singhu Border
]

coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in pts)
url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhi/1.0'})
try:
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        if data.get('code') == 'Ok':
            geom = [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
            print(f"SUCCESS: GT Karnal Road returned {len(geom)} street-snapped points!")
            print("First 3:", geom[:3])
            print("Last 3:", geom[-3:])
        else:
            print("OSRM error code:", data.get('code'))
except Exception as e:
    print("Error:", e)
