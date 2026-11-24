import urllib.request
import json

payload = {
    "origin": "Saket Bus Stop",
    "destination": "Dhaula Kuan",
    "departure_time": "08:30"
}
req = urllib.request.Request(
    "http://localhost:8000/api/v1/journey/plan",
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json"}
)
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))

for i, alt in enumerate(data.get("alternatives", [])):
    print(f"Card {i+1}: Badge={alt.get('badge')} | Fleet={alt.get('bus_fleet_type')}")
    print(f"  Dep={alt.get('departure_time_label')} -> Arr={alt.get('arrival_time_label')} ({alt.get('total_duration_mins')}m)")
    print(f"  Crowd Level={alt.get('crowd_level')} | Comfort={alt.get('comfort_label')}")
    stops = alt.get("timeline_stops", [])
    print(f"  Stops Count={len(stops)}")
    for s in stops:
        print(f"    - {s.get('eta_time')} | {s.get('stop_name')} | {s.get('seats_status')} | Action: {s.get('crowd_action')}")
