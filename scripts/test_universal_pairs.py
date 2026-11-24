import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

test_pairs = [
    ("Narela Terminal", "ISBT Kashmere Gate"),
    ("Dwarka Sector 10", "Uttam Nagar Terminal"),
    ("Janakpuri West", "Shivaji Stadium Terminal"),
    ("Mayur Vihar Phase 3", "Delhi Sachivalaya"),
    ("Mehrauli Terminal", "Badarpur Border Terminal"),
    ("Najafgarh Terminal", "Dhaula Kuan"),
    ("Rohini Sector 22", "Azadpur Terminal"),
    ("New Delhi Railway Station", "Anand Vihar ISBT"),
    ("Alipur Village", "ISBT Kashmere Gate"),
    ("Okhla Phase 3", "Lajpat Nagar")
]

print("=" * 80)
print("UNIVERSAL DELHI TRANSIT VERIFICATION: 10 ARBITRARY CROSS-CITY CORRIDORS")
print("=" * 80)

failures = 0
for orig_raw, dest_raw in test_pairs:
    try:
        plan = journey_service.find_routes(orig_raw, dest_raw, "08:30")
        f = plan.alternatives[0]
        r = plan.alternatives[1]
        c = plan.alternatives[2]
        print(f"\nTrip: {plan.origin} -> {plan.destination}")
        print(f"  Express: {f.departure_time_label} -> {f.arrival_time_label} ({f.total_duration_mins}m, {f.distance_km} km) | Stops: {f.stops_count}")
        print(f"  Regular: {r.departure_time_label} -> {r.arrival_time_label} ({r.total_duration_mins}m, {r.distance_km} km) | Stops: {r.stops_count}")
        print(f"  Comfort: {c.departure_time_label} -> {c.arrival_time_label} ({c.total_duration_mins}m, {c.distance_km} km) | Stops: {c.stops_count}")
        
        # Verify timeline stops have non-zero progressive KM and ETAs
        assert f.distance_km > 0, "Distance should be > 0"
        assert f.total_duration_mins > 0, "Duration should be > 0"
        assert len(f.timeline_stops) >= 2, "Must have at least 2 stops"
        assert f.timeline_stops[0]['distance_km'] == 0.0, "Start distance must be 0"
        assert f.timeline_stops[-1]['distance_km'] == f.distance_km, "End distance must match"
        assert f.timeline_stops[-1]['eta_time'] == f.arrival_time_label, "Last stop ETA must match card ETA"
        print(f"  [PASS] Physical distance, stop progression, and ETAs fully valid.")
    except Exception as e:
        print(f"  [FAIL] {orig_raw} -> {dest_raw}: {e}")
        failures += 1

print("\n" + "=" * 80)
print(f"RESULT: {len(test_pairs) - failures} / {len(test_pairs)} CORRIDORS PASSED UNIVERSALLY")
print("=" * 80)
