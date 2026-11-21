import urllib.request
import json

test_pairs = [
    ("Saket Metro Station", "Dhaula Kuan", "08:30"),
    ("Anand Vihar Isbt", "Shivaji Stadium", "18:00"),
    ("Kashmere Gate", "AIIMS", "09:00"),
    ("Hamdard Nagar / Sangam Vihar", "Badarpur Border", "17:30"),
    ("Rohini Sector 22", "Janakpuri West", "13:30"),
    ("Uttam Nagar Terminal", "Nehru Place", "08:00")
]

print("="*75)
print("TESTING DYNAMIC JOURNEY ENGINE FOR ALL ROUTES ACROSS DELHI")
print("="*75)

for orig, dest, dept in test_pairs:
    req = json.dumps({
        'origin': orig,
        'destination': dest,
        'departure_time': dept,
        'prefer_less_crowded': False
    }).encode('utf-8')

    try:
        r = urllib.request.Request('http://127.0.0.1:8000/api/v1/journey/plan', data=req, headers={'Content-Type': 'application/json'})
        resp = json.loads(urllib.request.urlopen(r).read())
        print(f"\nTrip: {resp['origin']} -> {resp['destination']} at {resp['departure_time']}")
        print(f"Options generated: {len(resp['alternatives'])}")
        for i, a in enumerate(resp['alternatives']):
            print(f"  Alt {i+1} [{a['badge']}]: Route {a['bus_routes']} | {a['total_duration_mins']} mins | {a['comfort_label']} | Stretch: {a['stretch_summary']}")
    except Exception as e:
        print(f"Error testing {orig} -> {dest}: {e}")
