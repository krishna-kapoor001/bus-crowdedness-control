import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/journey/plan"
data = json.dumps({
    "origin": "Saket Bus Stop",
    "destination": "Dhaula Kuan",
    "departure_time": "08:30",
    "prefer_less_crowded": False
}).encode('utf-8')

req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"=== Journey: {res['origin']} -> {res['destination']} at {res['departure_time']} ===")
        for i, alt in enumerate(res['alternatives']):
            print(f"\nOption {i+1} [{alt['badge']}]:")
            print(f"  Service Type: {alt.get('service_type')} | {alt.get('service_badge')}")
            print(f"  Duration: {alt['total_duration_mins']} mins (Time Saved: {alt.get('time_saved_mins')}m)")
            print(f"  Stops Count: {alt['stops_count']}")
            print(f"  Intermediate Stops: {alt.get('intermediate_stops')}")
            print(f"  Skipped Stops: {alt.get('skipped_stops')}")
except Exception as e:
    print("API Error:", e)
