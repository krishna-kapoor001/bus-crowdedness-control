import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

o = "Saket"
d = "Dhaula Kuan"
r1, r2 = journey_service._find_candidate_routes(o, d)
geom1 = journey_service.get_route_geometry(o, d, [r1, r2])
dist1 = sum(journey_service._haversine(p1[0], p1[1], p2[0], p2[1]) for p1, p2 in zip(geom1[:-1], geom1[1:]))
print(f"geom1: pts={len(geom1)}, dist={dist1:.2f} km")

reg_tuples, exp_tuples = journey_service._resolve_corridor_stops(o, d, dist1)
print(f"exp_tuples: len={len(exp_tuples)}")
for s in exp_tuples:
    print("  ", s)
