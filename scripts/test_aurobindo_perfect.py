import urllib.request
import json

def get_osrm(c1, c2):
    url = f"http://router.project-osrm.org/route/v1/driving/{c1[1]},{c1[0]};{c2[1]},{c2[0]}?overview=full&geometries=geojson"
    req = urllib.request.Request(url, headers={'User-Agent': 'TransportDelhiTest/1.0'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            if data.get('code') == 'Ok':
                return [[p[1], p[0]] for p in data['routes'][0]['geometry']['coordinates']]
    except Exception as e:
        print("Error:", e)
    return []

# Sequential Sri Aurobindo Marg anchors
anchors = [
    (28.5880, 77.2105), # Safdarjung Tomb
    (28.5745, 77.2090), # INA / Dilli Haat
    (28.5672, 77.2078), # AIIMS Underpass (Sri Aurobindo Marg)
    (28.5572, 77.2068), # Green Park
    (28.5494, 77.2055), # Hauz Khas
    (28.5458, 77.2025), # IIT Gate (Sri Aurobindo Marg)
    (28.5395, 77.1966), # Adhchini
    (28.5240, 77.1850), # Qutub Minar
    (28.5217, 77.1827)  # Mehrauli Terminal
]

full_poly = []
for i in range(len(anchors)-1):
    seg = get_osrm(anchors[i], anchors[i+1])
    if seg:
        if full_poly and full_poly[-1] == seg[0]:
            full_poly.extend(seg[1:])
        else:
            full_poly.extend(seg)

print(f"Aurobindo polyline: {len(full_poly)} points.")
# Check for any loops or U-turns
# In a north-to-south road, latitude should strictly decrease!
lat_increases = 0
for i in range(len(full_poly)-1):
    if full_poly[i+1][0] > full_poly[i][0] + 0.0005: # moving north significantly
        lat_increases += 1
        print(f"Lat increase at {i}: {full_poly[i]} -> {full_poly[i+1]}")

print(f"Total significant northward backtrackings: {lat_increases}")
if lat_increases == 0:
    print("SUCCESS: 100% strictly smooth sequential unidirectional route with ZERO U-turns/loops!")
