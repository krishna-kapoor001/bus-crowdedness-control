import json, urllib.request, time
import concurrent.futures

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Auditing all {len(stops)} stops against OSRM road types...")

expressway_keywords = ['expressway', 'express way', 'flyway', 'dnd', 'motorway', 'bypass', 'delhi - meerut', 'delhi-meerut', 'delhi-gurugram', 'nh24', 'nh 24', 'nh-24', 'nh 48', 'nh-48', 'nh 8', 'nh-8', 'delhi-dehradun']

def check_stop(s):
    lat = s['latitude']
    lon = s['longitude']
    url = f'http://router.project-osrm.org/nearest/v1/driving/{lon:.6f},{lat:.6f}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiExpAudit/1.0'})
        with urllib.request.urlopen(req, timeout=4) as r:
            data = json.loads(r.read().decode())
            if data.get('code') == 'Ok':
                wp = data['waypoints'][0]
                road_name = wp.get('name', '')
                if any(kw in road_name.lower() for kw in expressway_keywords):
                    return {
                        'name': s['name'],
                        'lat': lat,
                        'lon': lon,
                        'road_name': road_name,
                        'is_hub': s.get('is_major_hub', False)
                    }
    except Exception:
        pass
    return None

expressway_stops = []
# Run with thread pool of 10 workers for speed
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    futures = [executor.submit(check_stop, s) for s in stops]
    for future in concurrent.futures.as_completed(futures):
        res = future.result()
        if res:
            expressway_stops.append(res)
            print(f"FLAGGED: {res['name']} -> {res['road_name']} ({res['lat']}, {res['lon']})")

print(f"\nTOTAL FLAGGED EXPRESSWAY STOPS: {len(expressway_stops)}")
with open('data/flagged_expressway_stops.json', 'w', encoding='utf-8') as f:
    json.dump(expressway_stops, f, indent=2)
