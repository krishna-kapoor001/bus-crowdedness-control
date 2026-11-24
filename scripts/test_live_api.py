import urllib.request, json

req = urllib.request.Request(
    'http://localhost:8000/api/v1/journey/plan',
    data=json.dumps({'origin': 'Kashmere Gate', 'destination': 'AIIMS', 'departure_time': '08:30'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        print('HTTP Status 200 OK')
        print(f"Origin: {data['origin']} -> Dest: {data['destination']}")
        print(f"Alternatives: {len(data['alternatives'])}")
        alt = data['alternatives'][0]
        print(f"Alt 0: {alt['badge']} | {alt['departure_time_label']} -> {alt['arrival_time_label']} ({alt['total_duration_mins']}m)")
        print(f"Timeline stops count: {len(alt.get('timeline_stops', []))}")
        if alt.get('timeline_stops'):
            print("First stop:", alt['timeline_stops'][0]['stop_name'], alt['timeline_stops'][0]['eta_time'])
            print("Last stop:", alt['timeline_stops'][-1]['stop_name'], alt['timeline_stops'][-1]['eta_time'])
except Exception as e:
    print('Error:', e)
