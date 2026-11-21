import json, urllib.request, time

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Total stops: {len(stops)}")

# Let's check stops whose names or locations might be on expressways or let's test with OSRM
expressway_words = ['expressway', 'express way', 'dnd', 'flyover', 'nh-8', 'nh-24', 'nh-48', 'delhi-gurugram', 'bypass', 'barapullah']

# Let's sample stops and query OSRM to see what road they are snapped to
results = []
for i, s in enumerate(stops):
    name = s['name'].lower()
    lat = s['latitude']
    lon = s['longitude']
    
    # Check if name contains any keyword
    has_kw = any(w in name for w in expressway_words)
    
    # Or check if within bounding box of known expressways (NH-48, NH-9, DND, Barapullah, Outer Ring Road flyovers)
    in_exp_zone = (
        (28.52 <= lat <= 28.56 and 77.08 <= lon <= 77.13) or # NH-48
        (28.61 <= lat <= 28.635 and 77.27 <= lon <= 77.34) or # NH-9
        (28.57 <= lat <= 28.59 and 77.26 <= lon <= 77.31) or # DND
        (28.575 <= lat <= 28.592 and 77.22 <= lon <= 77.25)   # Barapullah
    )
    
    if has_kw or in_exp_zone:
        results.append(s)

print(f"Total stops in expressway corridors or matching keywords: {len(results)}")

# Let's query OSRM for these candidate stops to check road name
on_expressway = []
for s in results:
    lat, lon = s['latitude'], s['longitude']
    url = f'http://router.project-osrm.org/nearest/v1/driving/{lon:.6f},{lat:.6f}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiSnap/2.0'})
        with urllib.request.urlopen(req, timeout=3) as r:
            data = json.loads(r.read().decode())
            if data.get('code') == 'Ok':
                wp = data['waypoints'][0]
                road_name = wp.get('name', '')
                dist = wp.get('distance', 0)
                if any(w in road_name.lower() for w in ['expressway', 'flyway', 'dnd', 'bypass', 'barapullah', 'nh-8', 'nh-24', 'nh24', 'nh 24', 'nh 8', 'nh 48', 'nh-48']):
                    on_expressway.append({
                        'name': s['name'],
                        'lat': lat,
                        'lon': lon,
                        'road_name': road_name,
                        'dist': dist
                    })
    except Exception:
        pass
    time.sleep(0.05)

print(f"\nFOUND {len(on_expressway)} STOPS SNAPPED ONTO EXPRESSWAY / BYPASS ROAD:")
for item in on_expressway:
    print(f"  - {item['name']} -> snapped on '{item['road_name']}' at ({item['lat']}, {item['lon']})")
