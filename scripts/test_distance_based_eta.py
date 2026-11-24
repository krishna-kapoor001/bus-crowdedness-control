import json, math, os

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def format_time_12h(mins_from_midnight: int) -> str:
    mins = int(round(mins_from_midnight)) % (24 * 60)
    h = mins // 60
    m = mins % 60
    ampm = "PM" if h >= 12 else "AM"
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return f"{h12:02d}:{m:02d} {ampm}"

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops_meta = {s['name']: s for s in json.load(f)}

print(f"Loaded {len(stops_meta)} stops metadata.")

# Test with a real corridor: Saket to Dhaula Kuan
orig_name = "Saket"
dest_name = "Dhaula Kuan"
dep_time_str = "08:30"
dep_hour = 8

# Determine speed based on peak
is_peak = (7 <= dep_hour <= 10) or (17 <= dep_hour <= 20)
commercial_speed_kmh = 16.5 if is_peak else 22.0
speed_mps = (commercial_speed_kmh * 1000) / 3600 # ~4.58 m/s

print(f"Corridor Speed: {commercial_speed_kmh} km/h ({speed_mps:.2f} m/s) [Peak: {is_peak}]")
