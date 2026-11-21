import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/network/geojson'
with urllib.request.urlopen(url) as resp:
    data = json.loads(resp.read().decode('utf-8'))

features = {f['properties']['name'].lower(): f['geometry']['coordinates'] for f in data['features']}

checks = [
    ("Anand Vihar", 28.6483, 77.3178), # East Delhi
    ("Anand Vihar ISBT", 28.6483, 77.3178),
    ("Kashmere Gate", 28.6668, 77.2293), # North Delhi
    ("ISBT Kashmiri Gate", 28.6668, 77.2293),
    ("Safdarjung Hospital", 28.5701, 77.2078), # South Delhi Ring Road
    ("AIIMS", 28.5672, 77.2100),
    ("Dhaula Kuan", 28.5986, 77.1631),
    ("Palam Colony Flyover", 28.5910, 77.0850), # West Delhi / Palam
    ("Chhatarpur Metro Station", 28.5065, 77.1745), # South Delhi
    ("Saket Metro Station", 28.5204, 77.2026),
    ("Mayur Vihar Phase 1", 28.6041, 77.2944), # East Delhi
    ("Mayur Vihar Phase 3", 28.6018, 77.3273),
    ("Shivaji Stadium", 28.6327, 77.2156), # Connaught Place
    ("Connaught Place", 28.6327, 77.2156),
    ("Nehru Place Terminal", 28.5486, 77.2567),
    ("Uttam Nagar Terminal", 28.6255, 77.0661),
    ("Azadpur Terminal", 28.7070, 77.1790),
    ("Punjabi Bagh Terminal", 28.6754, 77.1404),
    ("Badarpur Border", 28.4983, 77.3046)
]

print("=== VERIFYING KEY STOPS ON MAP ===")
all_ok = True
for name, exp_lat, exp_lon in checks:
    coords = features.get(name.lower())
    if not coords:
        print(f"FAILED: '{name}' not found!")
        all_ok = False
        continue
    lon, lat = coords
    dist_err = ((lat - exp_lat)**2 + (lon - exp_lon)**2)**0.5
    status = "OK" if dist_err < 0.01 else "DISPLACED"
    print(f"  {name:25s} -> lat={lat:.4f}, lon={lon:.4f} [Expected: {exp_lat:.4f}, {exp_lon:.4f}] - {status}")
    if status != "OK":
        all_ok = False

print(f"\nFinal Check: {'ALL PASSED 100%' if all_ok else 'SOME DISPLACED'}")
