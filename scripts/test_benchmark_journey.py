import urllib.request
import json

req = json.dumps({
    'origin': 'Anand Vihar ISBT',
    'destination': 'Shivaji Stadium',
    'departure_time': '18:00',
    'prefer_less_crowded': False
}).encode('utf-8')

r = urllib.request.Request('http://127.0.0.1:8000/api/v1/journey/plan', data=req, headers={'Content-Type': 'application/json'})
resp = json.loads(urllib.request.urlopen(r).read())

print(f"Origin: {resp['origin']} -> Destination: {resp['destination']} ({resp['departure_time']})")
print(f"Alternatives count: {len(resp['alternatives'])}")
for i, a in enumerate(resp['alternatives']):
    print(f"--- Option {i+1} [{a['badge']}] ---")
    print(f"  Duration: {a['total_duration_mins']} mins")
    print(f"  Comfort: {a['comfort_label']}")
    print(f"  Crowd Level: {a['crowd_level']} (Score: {a['crowd_score']}/100)")
    print(f"  Stretch: {a['stretch_summary']}")
    print(f"  Routes: {a['bus_routes']}")
    print(f"  Explanation: {a['recommendation_explanation']}")
