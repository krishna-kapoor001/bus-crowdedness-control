import urllib.request
import urllib.parse
import json
import time

major_stops = [
    'DTC Bus Depot Yamuna Vihar',
    'Kashmere Gate ISBT',
    'Anand Vihar ISBT',
    'Sarai Kale Khan ISBT',
    'Dhaula Kuan',
    'Mehrauli Bus Terminal',
    'Shivaji Stadium Terminal',
    'Nehru Place Bus Terminal',
    'Azadpur Bus Terminal',
    'Najafgarh Bus Terminal',
    'Uttam Nagar Bus Terminal',
    'Shahdara Bus Terminal',
    'Nand Nagri Bus Depot',
    'Wazirpur Bus Depot',
    'Hasanpur Bus Depot',
    'Shadipur Bus Depot',
    'Kalkaji Bus Depot'
]

with open('data/processed/stop_profiles.json', encoding='utf-8') as f:
    current_stops = {s['name'].lower(): s for s in json.load(f)}

print(f"{'Stop Name':<30} | {'Current Lat/Lon':<22} | {'OSM Lat/Lon':<22} | {'Offset (m)'}")
print("-" * 88)

for name in major_stops:
    q = urllib.parse.quote(f"{name}, Delhi, India")
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransitAlign/1.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            if data:
                osm_lat = float(data[0]['lat'])
                osm_lon = float(data[0]['lon'])
                
                # Find matching current stop
                matched = None
                for k, v in current_stops.items():
                    clean_k = k.replace('terminal', '').replace('bus depot', '').replace('isbt', '').strip()
                    clean_n = name.lower().replace('terminal', '').replace('bus depot', '').replace('isbt', '').strip()
                    if clean_n in clean_k or clean_k in clean_n:
                        matched = v
                        break
                
                if matched:
                    cur_lat = matched['latitude']
                    cur_lon = matched['longitude']
                    import math
                    dist = math.hypot((cur_lat - osm_lat)*111000, (cur_lon - osm_lon)*100000)
                    print(f"{name:<30} | {cur_lat:.5f}, {cur_lon:.5f} | {osm_lat:.5f}, {osm_lon:.5f} | {dist:5.1f}m")
                else:
                    print(f"{name:<30} | {'Not found in db':<22} | {osm_lat:.5f}, {osm_lon:.5f} | N/A")
            else:
                print(f"{name:<30} | No match found on OSM")
        time.sleep(1)
    except Exception as e:
        print(f"{name:<30} | Error: {e}")
