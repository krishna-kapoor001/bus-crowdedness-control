import urllib.request
import json

pts = [
    (28.6675, 77.2285), # Kashmere Gate
    (28.6410, 77.2500), # Rajghat
    (28.6290, 77.2490), # ITO Ring Road
    (28.5871, 77.2591), # Sarai Kale Khan
    (28.5714, 77.2592), # Ashram
    (28.5700, 77.2400), # Lajpat Nagar
    (28.5690, 77.2134), # AIIMS
    (28.5702, 77.2078), # Safdarjung Hospital
    (28.5835, 77.1675), # Moti Bagh
    (28.6000, 77.1620)  # Dhaula Kuan
]

# Chunk into 2 parts of <= 6 waypoints each
p1 = pts[:6]
p2 = pts[5:]

def get_osrm(p_list):
    coords_str = ";".join(f"{p[1]:.6f},{p[0]:.6f}" for p in p_list)
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhi/1.0'})
    with urllib.request.urlopen(req, timeout=12) as resp:
        data = json.loads(resp.read().decode())
        return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]

try:
    g1 = get_osrm(p1)
    import time; time.sleep(0.5)
    g2 = get_osrm(p2)
    full_ring = g1 + g2[1:]
    print(f"SUCCESS: Ring Road returned {len(full_ring)} street-snapped points!")
except Exception as e:
    print("Error:", e)
