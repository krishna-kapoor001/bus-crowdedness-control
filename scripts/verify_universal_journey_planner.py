import sys, os
sys.path.insert(0, os.path.abspath('.'))
from backend.app.services.journey_service import journey_service

test_queries = [
    ("Kashmere Gate", "AIIMS", "08:30"),
    ("Anand Vihar", "Connaught Place", "08:30"),
    ("Janakpuri", "Dhaula Kuan", "09:15"),
    ("Saket", "IIT", "14:00"),
    ("Badarpur", "Nehru Place", "18:30"),
]

print("=" * 70)
print("VERIFYING UNIVERSAL JOURNEY PLANNER ACROSS DELHI")
print("=" * 70)

all_passed = True

for orig, dest, dep_time in test_queries:
    resp = journey_service.find_routes(orig, dest, departure_time=dep_time)
    print(f"\nQUERY: '{orig}' -> '{dest}' at {dep_time}")
    print(f"Resolved Stops: '{resp.origin}' -> '{resp.destination}'")
    print(f"Alternatives Returned: {len(resp.alternatives)}")
    
    if len(resp.alternatives) < 3:
        print(f"FAILED: Expected 3 alternatives, got {len(resp.alternatives)}")
        all_passed = False
        continue
        
    for alt in resp.alternatives:
        tl = alt.timeline_stops or []
        first_eta = tl[0]['eta_time'] if tl else 'N/A'
        last_eta = tl[-1]['eta_time'] if tl else 'N/A'
        
        print(f"  [{alt.badge:15s}] Bus: {alt.bus_routes[0]:8s} | {alt.departure_time_label} -> {alt.arrival_time_label} ({alt.total_duration_mins}m) | Stops: {alt.stops_count} | Comfort: {alt.comfort_label}")
        print(f"      Fleet: {alt.bus_fleet_type} | Seats: {alt.seating_capacity} | Total Cap: {alt.total_capacity} | Fare: {alt.fare_regular}")
        print(f"      Timeline First/Last: {first_eta} -> {last_eta} ({len(tl)} stops recorded)")
        
        # Verify Monotonicity
        prev_m = -1
        for st in tl:
            m = st['mins_from_start']
            if m < prev_m:
                print(f"      ERROR: Non-monotonic timestamp at {st['stop_name']} ({m} < {prev_m})")
                all_passed = False
            prev_m = m
            
        # Verify Arrival Matches Last Stop
        if tl and alt.arrival_time_label != last_eta:
            print(f"      ERROR: Alt arrival ({alt.arrival_time_label}) != Last stop ETA ({last_eta})")
            all_passed = False

if all_passed:
    print("\nALL 5 TEST PAIRS PASSED 100% MONOTONIC & PHYSICAL TIMETABLE CHECKS!")
    sys.exit(0)
else:
    print("\nFAILED: Issues found in verification!")
    sys.exit(1)
