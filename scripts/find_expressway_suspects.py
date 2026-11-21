import json
import urllib.request
import time

with open('data/stops_meta.json', encoding='utf-8') as f:
    stops = json.load(f)

# Let's inspect stops that might be on expressways or high-speed bypasses
# Or let's query OSRM for all stops along key corridors or check their nearest OSM tags
print(f"Total stops in meta: {len(stops)}")

# Let's check stops around NH-48 (Delhi-Gurgaon), NH-9/24 (DME), Ring Road flyovers, etc.
suspicious_corridors = [
    # NH-48 / Delhi-Gurgaon
    (28.50, 28.60, 77.08, 77.16, "NH-48 / Delhi-Gurugram"),
    # NH-9 / NH-24 / DME
    (28.60, 28.65, 77.27, 77.35, "NH-9 / NH-24 / Delhi-Meerut"),
    # DND Flyway
    (28.56, 28.59, 77.26, 77.32, "DND Flyway"),
    # Barapullah
    (28.57, 28.60, 77.21, 77.26, "Barapullah"),
    # Outer Ring Road / NH-1 / GTK
    (28.70, 28.78, 77.12, 77.18, "GTK / Mukarba Chowk"),
    # Dwarka Expressway
    (28.52, 28.57, 77.01, 77.08, "Dwarka Expressway")
]

suspect_stops = []
for s in stops:
    lat, lon = s['latitude'], s['longitude']
    for min_lat, max_lat, min_lon, max_lon, corr_name in suspicious_corridors:
        if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
            suspect_stops.append((corr_name, s))
            break

print(f"Stops in expressway/corridor zones: {len(suspect_stops)}")
for corr, s in suspect_stops[:30]:
    print(f"[{corr}] {s['name']} -> ({s['latitude']}, {s['longitude']})")
