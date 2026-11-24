import sys, os
sys.path.insert(0, '.')
from backend.app.services.journey_service import journey_service

# Test Saket to Dhaula Kuan
o = "Saket"
d = "Dhaula Kuan"
road_km = 10.7
dep_time = "08:30"

reg_tuples, exp_tuples = journey_service._resolve_corridor_stops(o, d, road_km)
print(f"Saket -> Dhaula Kuan: road_km={road_km}")
print(f"Exp stops ({len(exp_tuples)}): {[s[0] for s in exp_tuples]}")
print(f"Reg stops ({len(reg_tuples)}): {[s[0] for s in reg_tuples]}")

# 1. Fastest (Express) at 08:30
dep1, arr1, dur1, tl1 = journey_service._build_timeline(
    exp_tuples, "08:30", road_km, 22.0, 0.8, 72, True
)
print(f"\n1. FASTEST (Express): {dep1} -> {arr1} ({dur1}m) | {len(tl1)} stops")

# 2. Regular (All Stops) at 08:30
dep2, arr2, dur2, tl2 = journey_service._build_timeline(
    reg_tuples, "08:30", road_km, 17.0, 0.6, 55, True
)
print(f"2. DIRECT (All Stops): {dep2} -> {arr2} ({dur2}m) | {len(tl2)} stops")

# 3. Comfort (Shift +20m) at 08:50 (traffic clearer at 24 km/h)
dep3, arr3, dur3, tl3 = journey_service._build_timeline(
    exp_tuples, "08:50", road_km, 24.0, 0.7, 24, False
)
print(f"3. COMFORT (Seats Available): {dep3} -> {arr3} ({dur3}m) | {len(tl3)} stops")
