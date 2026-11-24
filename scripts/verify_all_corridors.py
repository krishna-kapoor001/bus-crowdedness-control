import urllib.request
import json
import time

corridors = [
    ("Saket Crossing", "Dhaula Kuan", "08:30"),
    ("Anand Vihar ISBT", "Shivaji Stadium", "09:00"),
    ("Kashmere Gate ISBT", "AIIMS", "17:30"),
    ("Badarpur Border", "Nehru Place", "10:15"),
    ("Punjabi Bagh Terminal", "Karol Bagh Metro", "18:00")
]

all_passed = True
for orig, dest, dep_time in corridors:
    t0 = time.time()
    data = json.dumps({"origin": orig, "destination": dest, "departure_time": dep_time}).encode()
    req = urllib.request.Request("http://localhost:8000/api/v1/journey/plan", data=data, headers={"Content-Type": "application/json"})
    try:
        resp = urllib.request.urlopen(req)
        res = json.loads(resp.read())
        elapsed = (time.time() - t0) * 1000
        alts = res.get("alternatives", [])
        if len(alts) < 1:
            print(f"FAILED {orig} -> {dest}: No alternatives")
            all_passed = False
            continue
        a = alts[0]
        stops = a.get("timeline_stops", [])
        coords = a.get("route_coordinates", [])
        print(f"PASS [{elapsed:.1f}ms] {orig} -> {dest} at {dep_time}")
        print(f"     Route: {a['bus_routes']} | Duration: {a['total_duration_mins']}m | Dist: {a['distance_km']}km | Stops: {len(stops)} | Coords: {len(coords)}")
    except Exception as e:
        print(f"FAILED {orig} -> {dest}: {e}")
        all_passed = False

if all_passed:
    print("\nALL 5 CORRIDOR TESTS PASSED WITH 100% SUCCESS!")
else:
    print("\nSOME TESTS FAILED!")
