import json
import csv
import math

# Load gtfs stops
gtfs = []
with open("data/gtfs_delhi_stops.txt", "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        gtfs.append((float(row['stop_lat']), float(row['stop_lon']), row['stop_name']))

print(f"Loaded {len(gtfs)} GTFS surveyed stops.")

# Load stop_profiles.json
with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops = json.load(f)

print(f"Auditing {len(stops)} stops in stop_profiles.json...")

outside_delhi = []
far_from_gtfs = []
coarse = []

for s in stops:
    lat = s['latitude']
    lon = s['longitude']
    name = s['name']
    
    # Check Delhi boundary (lat 28.40 to 28.88, lon 76.84 to 77.34)
    if not (28.40 <= lat <= 28.90 and 76.80 <= lon <= 77.36):
        outside_delhi.append((name, lat, lon))
        
    # Check decimals
    lat_s = str(lat)
    lon_s = str(lon)
    lat_dec = len(lat_s.split('.')[1]) if '.' in lat_s else 0
    lon_dec = len(lon_s.split('.')[1]) if '.' in lon_s else 0
    if lat_dec <= 3 or lon_dec <= 3:
        coarse.append((name, lat, lon))
        
    # Find distance to nearest GTFS stop
    min_d = float('inf')
    nearest_gtfs = None
    for g_lat, g_lon, g_name in gtfs:
        # approximate distance in meters
        d = math.hypot((lat - g_lat)*111000, (lon - g_lon)*111000*math.cos(math.radians(lat)))
        if d < min_d:
            min_d = d
            nearest_gtfs = (g_name, g_lat, g_lon)
            
    if min_d > 250: # More than 250m from ANY surveyed bus stop
        far_from_gtfs.append((name, lat, lon, min_d, nearest_gtfs))

print(f"\n1. Outside Delhi count: {len(outside_delhi)}")
for o in outside_delhi:
    print("   Outside:", o)

print(f"\n2. Coarse coordinates (<=3 decimals): {len(coarse)}")
for c in coarse:
    print("   Coarse:", c)

print(f"\n3. Stops far (>250m) from any GTFS surveyed stop: {len(far_from_gtfs)}")
for f in far_from_gtfs:
    print(f"   {f[0]} ({f[1]}, {f[2]}): {f[3]:.1f}m away from nearest GTFS '{f[4][0]}' at ({f[4][1]}, {f[4][2]})")
