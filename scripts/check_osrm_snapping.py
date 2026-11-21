import urllib.request
import json

test_stops = [
    ("Shiv Murti", 28.535888, 77.112206),
    ("Shiv Murti II NH 8 Dawrcka More", 28.534865, 77.108664),
    ("Rangpuri", 28.54393, 77.117843),
    ("Mahipal Pur Village", 28.546634, 77.124816),
    ("NHW 24 crossing", 28.626679, 77.316545),
    ("National Highway 24 Crossing", 28.627179, 77.318156),
    ("GTK Bypass", 28.738164, 77.154329),
    ("Pusta Crossing Akhardham Temple", 28.612282, 77.282372),
    ("Samaspur Jagir Village", 28.615427, 77.285596),
    ("Mayur Vihar Phase II", 28.620125, 77.305427)
]

for name, lat, lon in test_stops:
    url = f"http://router.project-osrm.org/nearest/v1/driving/{lon},{lat}?number=3"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransportCheck/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode())
            snapped = res['waypoints'][0]
            road_name = snapped.get('name', 'Unnamed')
            dist = snapped.get('distance', 0)
            print(f"{name}: snapped to '{road_name}' (distance: {dist:.1f}m, coords: {snapped['location'][1]:.6f}, {snapped['location'][0]:.6f})")
    except Exception as e:
        print(f"{name}: error {e}")
