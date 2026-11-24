import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

test_hours = ["06:00", "08:30", "10:00", "14:00", "18:30", "20:00", "22:30"]
orig = "Saket Bus Stop"
dest = "Dhaula Kuan"

print(f"=== TESTING ETA ACROSS 24 HOURS: {orig} -> {dest} ===")
for t in test_hours:
    plan = journey_service.find_routes(orig, dest, t)
    f = plan.alternatives[0]
    r = plan.alternatives[1]
    c = plan.alternatives[2]
    print(f"Time {t}:")
    print(f"  Express: {f.departure_time_label} -> {f.arrival_time_label} ({f.total_duration_mins}m, {f.distance_km} km) | Crowd={f.comfort_label}")
    print(f"  Regular: {r.departure_time_label} -> {r.arrival_time_label} ({r.total_duration_mins}m, {r.distance_km} km) | Crowd={r.comfort_label}")
    print(f"  Comfort: {c.departure_time_label} -> {c.arrival_time_label} ({c.total_duration_mins}m, {c.distance_km} km) | Crowd={c.comfort_label}")
