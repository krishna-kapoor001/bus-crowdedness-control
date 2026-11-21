import urllib.request
import json

def get_osrm_route(coords):
    coord_str = ";".join([f"{lon:.6f},{lat:.6f}" for lat, lon in coords])
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_str}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiAudit/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok' and data.get('routes'):
                # Return list of [lat, lon]
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print("OSRM error:", e)
    return None

# Test airport corridor with Rajokri anchor
stops = [
    (28.60005, 77.162017), # Dhaula Kuan
    (28.587833, 77.170333), # Satya Niketan
    (28.546733, 77.125),    # Mahipal Pur Crossing
    (28.5468, 77.1237),     # Mahipal Pur
    (28.536033, 77.1119),   # Shiv Murti
    (28.5140, 77.0950),     # Rajokri Flyover
    (28.5217, 77.082117)    # Kapashera Border
]

route = get_osrm_route(stops)
if route:
    print(f"Success! Route has {len(route)} points.")
    lons = [p[1] for p in route]
    print(f"Min lon: {min(lons):.5f}, Max lon: {max(lons):.5f}")
    if min(lons) >= 77.08:
        print("PERFECT: Route stays entirely on NH-48 / Rajokri without entering Dwarka!")
    else:
        print("Dips to:", min(lons))
else:
    print("Failed to get route.")
