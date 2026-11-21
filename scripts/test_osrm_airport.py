import urllib.request
import json

# Stops: Dhaula Kuan -> Satya Niketan -> Mahipal Pur -> Kapashera Border
waypoints = [
    (77.16315, 28.598667), # Dhaula Kuan (lon, lat)
    (77.170333, 28.587833), # Satya Niketan
    (77.126733, 28.545867), # Mahipal Pur
    (77.082424, 28.521848)  # Kapashera Border
]

coords_str = ";".join(f"{lon:.6f},{lat:.6f}" for lon, lat in waypoints)
url = f"https://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"

print("Querying OSRM for street-snapped route...")
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
try:
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        if data.get('code') == 'Ok':
            route = data['routes'][0]
            geom = route['geometry']['coordinates']
            print(f"SUCCESS! Retrieved {len(geom)} street-snapped coordinates.")
            # Convert [lon, lat] to [lat, lon] for Leaflet
            leaflet_coords = [[round(pt[1], 6), round(pt[0], 6)] for pt in geom]
            print("First 5 Leaflet coords:", leaflet_coords[:5])
            print("Middle 5 Leaflet coords:", leaflet_coords[len(leaflet_coords)//2 - 2 : len(leaflet_coords)//2 + 3])
            print("Last 5 Leaflet coords:", leaflet_coords[-5:])
except Exception as e:
    print("OSRM error:", e)
