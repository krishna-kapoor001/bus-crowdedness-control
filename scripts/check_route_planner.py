import urllib.request
import json

def test():
    data = json.dumps({'origin': 'Saket Crossing', 'destination': 'Dhaula Kuan', 'departure_time': '08:30'}).encode()
    req = urllib.request.Request('http://localhost:8000/api/v1/journey/plan', data=data, headers={'Content-Type': 'application/json'})
    res = json.loads(urllib.request.urlopen(req).read())
    alt2 = res['alternatives'][1]
    print(f"Alt 2 [{alt2['badge']}] ({alt2['bus_routes'][0]}): {len(alt2['timeline_stops'])} stops total:")
    for s in alt2['timeline_stops'][:6]:
        print(f"  Stop {s['stop_sequence']}: {s['stop_name']} | Time={s['eta_time']} | +{s['mins_from_start']}m | {s['distance_km']}km | Rush={s['crowd_level']}")

test()
