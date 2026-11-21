import urllib.request
import json

test_pts = [
    ('Mehrauli Terminal', 28.5216, 77.1830),
    ('Shivaji Stadium', 28.6289, 77.2113),
    ('Kashmere Gate ISBT', 28.6687, 77.2304),
    ('Badarpur Border', 28.4984, 77.3045),
    ('Najafgarh Terminal', 28.6135, 76.9860)
]

for name, lat, lon in test_pts:
    url = f'http://router.project-osrm.org/nearest/v1/driving/{lon},{lat}'
    req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitAcademicValidator/1.0'})
    try:
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read().decode())
        wp = data['waypoints'][0]
        street = wp.get('name', 'Unknown')
        snap_lon, snap_lat = wp['location']
        print(f'{name} -> snapped to road \"{street}\" at ({snap_lat:.5f}, {snap_lon:.5f})')
    except Exception as e:
        print(f'{name} error:', e)
