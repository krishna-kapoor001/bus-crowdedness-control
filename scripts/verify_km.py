import urllib.request, json
req = urllib.request.Request("http://localhost:8000/api/v1/journey/plan", data=json.dumps({"origin":"Saket Bus Stop","destination":"Dhaula Kuan","departure_time":"08:30"}).encode(), headers={"Content-Type":"application/json"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
for i, a in enumerate(data.get("alternatives", [])):
    print(f"Card {i+1}: Badge={a.get('badge')} | Dist={a.get('distance_km')} km | Dur={a.get('total_duration_mins')}m | Dep={a.get('departure_time_label')} -> Arr={a.get('arrival_time_label')}")
    print(f"  First Stop Dist: {a['timeline_stops'][0]['distance_km']} km | Last Stop Dist: {a['timeline_stops'][-1]['distance_km']} km")
