import urllib.request, json

pairs = [
    ('Rohini', 'Janakpuri', '08:30'),
    ('Narela', 'Azadpur', '08:30'),
    ('Saket', 'Dhaula Kuan', '08:30'),
    ('Mayur Vihar', 'Connaught Place', '08:30'),
    ('Dwarka', 'Karol Bagh', '09:00')
]

for orig, dest, dep_time in pairs:
    req = urllib.request.Request(
        'http://localhost:8000/api/v1/journey/plan',
        data=json.dumps({'origin': orig, 'destination': dest, 'departure_time': dep_time}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        fastest = data['alternatives'][0]
        regular = data['alternatives'][1]
        print(f"=== {orig} -> {dest} ===")
        print(f"  Resolved: {data['origin']} -> {data['destination']}")
        print(f"  Express:  {fastest['departure_time_label']} -> {fastest['arrival_time_label']} ({fastest['total_duration_mins']}m) | Stops: {len(fastest.get('timeline_stops', []))}")
        print(f"  Regular:  {regular['departure_time_label']} -> {regular['arrival_time_label']} ({regular['total_duration_mins']}m) | Stops: {len(regular.get('timeline_stops', []))}")
        print(f"  Time Saved by Express: {regular['total_duration_mins'] - fastest['total_duration_mins']} mins\n")
