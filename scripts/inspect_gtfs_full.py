import csv
import json
import re

# Bounding box for Delhi NCT strictly:
# Delhi NCT boundaries:
# Lat: ~28.404 to 28.883
# Lon: ~76.838 to 77.348 (east of Yamuna/Noida border is Uttar Pradesh, south is Haryana, west is Haryana, north is Haryana)

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    gtfs_stops = list(reader)

print(f"Total rows in gtfs_delhi_stops.txt: {len(gtfs_stops)}")

# Inspect stop_name patterns
outside = []
inside = []
depots_terminals = []
regular_stops = []

for row in gtfs_stops:
    name = row['stop_name'].strip()
    lat = float(row['stop_lat'])
    lon = float(row['stop_lon'])
    
    # Check outside keywords
    is_outside_keyword = any(k in name.lower() for k in ['noida', 'gurgaon', 'gurugram', 'ghaziabad', 'faridabad', 'bahadurgarh', 'sonipat'])
    
    # Strict Delhi NCT bounding box:
    # 28.40 <= lat <= 28.89 and 76.84 <= lon <= 77.35
    is_in_bbox = (28.40 <= lat <= 28.89) and (76.84 <= lon <= 77.35)
    
    if is_outside_keyword or not is_in_bbox:
        outside.append((name, lat, lon))
    else:
        inside.append({
            'stop_id': row['stop_id'],
            'stop_code': row.get('stop_code', ''),
            'name': name,
            'latitude': lat,
            'longitude': lon,
            'is_hub': any(t in name.lower() for t in ['terminal', 'depot', 'isbt', 'stand'])
        })
        if any(t in name.lower() for t in ['terminal', 'depot', 'isbt', 'stand']):
            depots_terminals.append(name)
        else:
            regular_stops.append(name)

print(f"Inside Delhi NCT: {len(inside)} stops")
print(f"Outside Delhi NCT / NCR: {len(outside)} stops (Examples: {outside[:5]})")
print(f"Major Bus Stands / Terminals / Depots: {len(depots_terminals)}")
print(f"Regular Bus Stops: {len(regular_stops)}")

# Check duplicate names:
unique_names = set(s['name'] for s in inside)
print(f"Unique stop names inside Delhi: {len(unique_names)}")
