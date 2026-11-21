import urllib.request
import urllib.parse
import json
import time

stops_to_check = [
    "ISBT Kashmere Gate Delhi",
    "ISBT Anand Vihar Delhi",
    "Sarai Kale Khan ISBT Delhi",
    "Shivaji Stadium Bus Terminal Delhi",
    "Nehru Place Bus Terminal Delhi",
    "Azadpur Bus Terminal Delhi",
    "Uttam Nagar Bus Terminal Delhi",
    "Dhaula Kuan Bus Stop Delhi",
    "AIIMS Bus Stop Delhi",
    "Safdarjung Hospital Bus Stop Delhi",
    "Moti Bagh Bus Stop Delhi",
    "Satya Niketan Bus Stop Delhi",
    "Mahipalpur Bus Stop Delhi",
    "Kapashera Border Delhi",
    "Saket Metro Station Delhi",
    "Chhatarpur Metro Station Delhi"
]

print("Querying Nominatim for OpenStreetMap ground truth...")
for name in stops_to_check:
    q = urllib.parse.quote(name)
    url = f"https://nominatim.openstreetmap.org/search?q={q}&format=json&limit=1"
    req = urllib.request.Request(url, headers={'User-Agent': 'DelhiTransportEvaluation/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data:
                res = data[0]
                print(f"OSM: '{name}' -> ({float(res['lat']):.6f}, {float(res['lon']):.6f}) | {res['display_name'][:50]}")
            else:
                print(f"OSM: '{name}' -> NOT FOUND")
        time.sleep(1.0) # Respect Nominatim 1 req/sec policy
    except Exception as e:
        print(f"OSM: '{name}' -> Error: {e}")
