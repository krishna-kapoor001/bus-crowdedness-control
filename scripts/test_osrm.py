import urllib.request, json, time

corridors_wps = {
    'corridor-mb': [
        [28.5195, 77.1818], [28.5220, 77.1980], [28.5204, 77.2015],
        [28.5180, 77.2320], [28.5126, 77.2485], [28.5030, 77.2880],
        [28.4984, 77.3045]
    ],
    'corridor-airport': [
        [28.5921, 77.1614], [28.5860, 77.1680], [28.5680, 77.1500],
        [28.5444, 77.1278], [28.5330, 77.1120], [28.5255, 77.0865]
    ],
    'corridor-aurobindo': [
        [28.5880, 77.2100], [28.5672, 77.2100], [28.5560, 77.2060],
        [28.5435, 77.2060], [28.5360, 77.1950], [28.5245, 77.1855],
        [28.5195, 77.1818]
    ],
    'corridor-mathura': [
        [28.6360, 77.2430], [28.6200, 77.2440], [28.5886, 77.2530],
        [28.5700, 77.2550], [28.5410, 77.2830], [28.5350, 77.2800],
        [28.4984, 77.3045]
    ],
    'corridor-gtk': [
        [28.7070, 77.1790], [28.7180, 77.1750], [28.7260, 77.1680],
        [28.7520, 77.1550], [28.7990, 77.1330], [28.8250, 77.1200]
    ]
}

for cid, wps in corridors_wps.items():
    locs = ';'.join(f'{pt[1]:.5f},{pt[0]:.5f}' for pt in wps)
    url = f'http://router.project-osrm.org/route/v1/driving/{locs}?overview=full&geometries=geojson'
    req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitApp/1.0'})
    try:
        res = urllib.request.urlopen(req, timeout=10)
        data = json.loads(res.read().decode())
        if data.get('code') == 'Ok':
            pts = data['routes'][0]['geometry']['coordinates']
            print(f'{cid}: routed successfully with {len(pts)} road points!')
        else:
            print(f'{cid}: OSRM returned code {data.get("code")}')
    except Exception as e:
        print(f'{cid} error:', e)
    time.sleep(0.5)
