import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("backend"))

import math
from backend.app.services.journey_service import journey_service

test_corridors = [
    ("Saket Bus Stop", "Dhaula Kuan"),
    ("Anand Vihar ISBT Main Road", "Shivaji Stadium"),
    ("Kashmere Gate", "AIIMS"),
    ("Hamdard Nagar / Sangam Vihar", "Badarpur Border")
]

for orig, dest in test_corridors:
    o_match = journey_service._resolve_stop(orig)
    d_match = journey_service._resolve_stop(dest)
    o_info = journey_service.stops_meta.get(o_match, {})
    d_info = journey_service.stops_meta.get(d_match, {})
    o_lat, o_lon = o_info.get('latitude', 0), o_info.get('longitude', 0)
    d_lat, d_lon = d_info.get('latitude', 0), d_info.get('longitude', 0)
    straight = journey_service._haversine(o_lat, o_lon, d_lat, d_lon)
    geom = journey_service.get_route_geometry(o_match, d_match, [])
    poly_dist = 0.0
    for i in range(len(geom)-1):
        poly_dist += journey_service._haversine(geom[i][0], geom[i][1], geom[i+1][0], geom[i+1][1])
    
    plan = journey_service.find_routes(orig, dest, "08:30")
    print(f"\n=== {o_match} -> {d_match} ===")
    print(f"  Straight: {straight:.2f} km | Polyline: {poly_dist:.2f} km")
    for a in plan.alternatives:
        last_d = a.timeline_stops[-1].get('distance_km') if a.timeline_stops else None
        print(f"  [{a.badge:<15}] Dep={a.departure_time_label} -> Arr={a.arrival_time_label} ({a.total_duration_mins}m) | Stops={a.stops_count} | LastStopDist={last_d} km")
