import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

import urllib.request, json
from backend.app.services.journey_service import journey_service

# Test Saket to Dhaula Kuan
stops = ['Saket', 'Mehrauli Terminal', 'Munirka Village', 'Sarojini Nagar Depot', 'Dhaula Kuan']
coords = []
for s in stops:
    info = journey_service.stops_meta.get(s, {})
    coords.append((info['latitude'], info['longitude']))

print("Stops coordinates:")
for s, (lat, lon) in zip(stops, coords):
    print(f"  {s:<25}: lat={lat:.6f}, lon={lon:.6f}")

# Query OSRM with all stop coordinates
coords_str = ";".join([f"{lon:.6f},{lat:.6f}" for lat, lon in coords])
url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?overview=full&geometries=geojson"
req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransportPlanner/1.0'})

try:
    with urllib.request.urlopen(req, timeout=4) as resp:
        data = json.loads(resp.read().decode())
        route = data['routes'][0]
        osrm_dist_km = route['distance'] / 1000.0
        osrm_duration_min = route['duration'] / 60.0
        pts_count = len(route['geometry']['coordinates'])
        print(f"\n[OSRM Real Street Network Result]")
        print(f"  Real Road Distance: {osrm_dist_km:.2f} km")
        print(f"  Free-Flow Duration: {osrm_duration_min:.1f} mins (cars)")
        print(f"  Road Geometry Points: {pts_count} street-snapped points")
except Exception as e:
    print(f"OSRM Query error: {e}")
