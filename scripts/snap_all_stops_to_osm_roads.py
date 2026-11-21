import json
import sqlite3
import urllib.request
import concurrent.futures
import time
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')
DB_PATH = os.path.join(DATA_DIR, 'flowpulse.db')
stops_file = os.path.join(PROCESSED_DIR, 'stop_profiles.json')

with open(stops_file, 'r', encoding='utf-8') as f:
    stops = json.load(f)

def snap_stop(s):
    lat = s['latitude']
    lon = s['longitude']
    name = s['name']
    url = f'http://router.project-osrm.org/nearest/v1/driving/{lon:.5f},{lat:.5f}'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitRoadSnap/1.0'})
        res = urllib.request.urlopen(req, timeout=5)
        data = json.loads(res.read().decode())
        if data.get('code') == 'Ok':
            wp = data['waypoints'][0]
            snap_lon, snap_lat = wp['location']
            # Only update if within 150m of original coordinate (to prevent jumping across corridors)
            dlat = abs(snap_lat - lat)
            dlon = abs(snap_lon - lon)
            if dlat < 0.002 and dlon < 0.002:
                s['latitude'] = round(snap_lat, 5)
                s['longitude'] = round(snap_lon, 5)
    except Exception as e:
        pass
    return s

print(f"Snapping {len(stops)} stops to OpenStreetMap street network in parallel...", flush=True)
t0 = time.time()
with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    snapped_stops = list(executor.map(snap_stop, stops))

print(f"Completed road snapping in {time.time()-t0:.2f}s", flush=True)

# Save to stop_profiles.json
with open(stops_file, 'w', encoding='utf-8') as f:
    json.dump(snapped_stops, f, indent=2, ensure_ascii=False)

# Save to stops_meta.json
meta_file = os.path.join(DATA_DIR, 'stops_meta.json')
with open(meta_file, 'w', encoding='utf-8') as f:
    json.dump(snapped_stops, f, indent=2, ensure_ascii=False)

# Update database
if os.path.exists(DB_PATH):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for s in snapped_stops:
        cur.execute("UPDATE stops SET latitude = ?, longitude = ? WHERE name = ?", (s['latitude'], s['longitude'], s['name']))
    conn.commit()
    conn.close()
    print("Database updated with road-snapped coordinates.")
