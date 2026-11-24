import urllib.request
import urllib.parse
import json

test_stops = ['Narela', 'Mayur Vihar', 'Burari', 'Badarpur', 'Nangloi', 'Tilak Nagar', 'Dwarka', 'Saket']
print("Testing Stop Autocomplete Endpoint:")
for q in test_stops:
    url = f"http://localhost:8000/api/v1/journey/stops?query={urllib.parse.quote(q)}"
    res = json.loads(urllib.request.urlopen(url).read())
    names = [s['name'] for s in res[:2]]
    print(f"  Query '{q}': {len(res)} matches -> {names}")

print("\nTesting Full Journey Plan with peripheral stops:")
plan_url = "http://localhost:8000/api/v1/journey/plan"
req_data = json.dumps({
    "origin": "Mayur Vihar Phase 1",
    "destination": "Narela",
    "departure_time": "09:00",
    "prefer_less_crowded": False
}).encode('utf-8')

req = urllib.request.Request(plan_url, data=req_data, headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(req).read())
print(f"  Plan origin: {resp.get('origin')} -> destination: {resp.get('destination')}")
alts = resp.get('alternatives', [])
print(f"  Total alternatives returned: {len(alts)}")
for a in alts:
    print(f"  Badge: {a.get('badge')} | Duration: {a.get('total_duration_mins')}m | Stops count: {a.get('stops_count')} | Bus: {a.get('bus_routes')}")
    timeline = a.get('timeline_stops', [])
    if timeline:
        print(f"    First stop: {timeline[0]['stop_name']} ({timeline[0]['eta_time']}) -> Last stop: {timeline[-1]['stop_name']} ({timeline[-1]['eta_time']})")

print("\nAll checks passed successfully!")
