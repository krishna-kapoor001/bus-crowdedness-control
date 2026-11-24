import urllib.request, json

req = urllib.request.Request(
    'http://127.0.0.1:8000/api/v1/journey/plan',
    data=json.dumps({
        'origin': 'Saket Bus Stop',
        'destination': 'Dhaula Kuan',
        'departure_time': '08:30',
        'prefer_less_crowded': False
    }).encode(),
    headers={'Content-Type': 'application/json'}
)

resp = json.loads(urllib.request.urlopen(req).read().decode())
alt = resp['alternatives'][0]
print("Alt 0 ID:", alt['id'])
print(f"Time: {alt['departure_time_label']} -> {alt['arrival_time_label']} ({alt['total_duration_mins']} mins)")
print(f"Fleet: {alt['bus_fleet_type']} | Cap: {alt['total_capacity']} ({alt['seating_capacity']} seats)")
print(f"Fare: {alt['fare_regular']} | Pink Pass: {alt['fare_pink_pass']}")
print("\nTimeline stops sample:")
for st in alt.get('timeline_stops', [])[:5]:
    print(f"  {st['eta_time']} (+{st['mins_from_start']}m) | {st['stop_name']} | {st['onboard_pax']}/65 pax ({st['seats_status']}) | {st['crowd_action']}")
