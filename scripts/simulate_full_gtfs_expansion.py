import csv
import json
import math
import re

# Load 28 corridors to associate each stop with its nearest arterial corridor
with open('data/processed/corridors_routed.json', 'r', encoding='utf-8') as f:
    corridors = json.load(f)

# Load existing 428 stops to preserve verified OSM centroids (like Shahdara Terminal, Yamuna Vihar Depot)
with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    existing_stops = json.load(f)
existing_map = {s['name'].lower().strip(): s for s in existing_stops}

# Load GTFS stops
with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs_rows = list(csv.DictReader(f))

print(f"Total GTFS stops to process: {len(gtfs_rows)}")

def clean_stop_name(name):
    # Remove Metro Station references as requested by user
    name = re.sub(r'\bMetro\s+Station\b', 'Bus Stop', name, flags=re.IGNORECASE)
    name = re.sub(r'\bMetro\s+Stn\b', 'Bus Stop', name, flags=re.IGNORECASE)
    name = re.sub(r'\(Metro\s+Station\)', 'Bus Stop', name, flags=re.IGNORECASE)
    name = re.sub(r'\(Metro\)', '', name, flags=re.IGNORECASE)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

all_stops = []
seen_names = {}

for idx, r in enumerate(gtfs_rows):
    raw_name = r['stop_name'].strip()
    c_name = clean_stop_name(raw_name)
    lat = float(r['stop_lat'])
    lon = float(r['stop_lon'])
    
    # If stop already exists in our verified 428 profiles, prioritize the verified OSM coordinate
    key = c_name.lower()
    if key in existing_map:
        ex = existing_map[key]
        lat = ex['latitude']
        lon = ex['longitude']
        corridor = ex.get('corridor', 'Delhi Transit Region')
        is_hub = ex.get('is_major_hub', False)
        boardings = ex.get('monthly_boardings', 2500)
        alightings = ex.get('monthly_alightings', 2400)
    else:
        # Determine if it's a Major Bus Stand / Depot / Terminal
        is_hub = any(t in c_name.lower() for t in ['terminal', 'depot', 'isbt', 'bus stand'])
        
        # Find closest corridor
        closest_corr = "Delhi Transit Region"
        min_dist = float('inf')
        for c in corridors:
            pts = c.get('coordinates', [])
            for pt in pts[::3]:
                d = math.hypot((lat - pt[0])*111000, (lon - pt[1])*111000)
                if d < min_dist:
                    min_dist = d
                    closest_corr = c.get('name', 'Delhi Transit Region').split('(')[0].strip()
        corridor = closest_corr if min_dist < 4000 else "Delhi Transit Region"
        boardings = 3200 if is_hub else 850
        alightings = 3100 if is_hub else 800

    all_stops.append({
        'id': idx + 1,
        'stop_id': r.get('stop_id'),
        'name': c_name,
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'corridor': corridor,
        'monthly_boardings': boardings,
        'monthly_alightings': alightings,
        'is_major_hub': is_hub
    })

print(f"Generated {len(all_stops)} total stops!")
hubs = [s for s in all_stops if s['is_major_hub']]
locals = [s for s in all_stops if not s['is_major_hub']]
print(f"  Major Bus Stands / Terminals (Black Dots): {len(hubs)}")
print(f"  Regular Bus Stops (Blue Dots): {len(locals)}")

# Check coordinate precision
coarse = [s for s in all_stops if len(str(s['latitude']).split('.')[1]) <= 3 or len(str(s['longitude']).split('.')[1]) <= 3]
print(f"  Coarse coordinates count: {len(coarse)}")
outside = [s for s in all_stops if not (28.40 <= s['latitude'] <= 28.90 and 76.83 <= s['longitude'] <= 77.35)]
print(f"  Outside Delhi count: {len(outside)}")
metro_remain = [s for s in all_stops if 'metro' in s['name'].lower()]
print(f"  Remaining 'Metro' in stop names: {len(metro_remain)}")
