import urllib.request
import lzma
import json
import time

url = "https://download.bbbike.org/osm/bbbike/NewDelhi/NewDelhi.osm.geojson.xz"
print(f"Streaming download from {url} ...")
t0 = time.time()

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
with urllib.request.urlopen(req, timeout=120) as resp:
    compressed_bytes = resp.read()

print(f"Downloaded {len(compressed_bytes) / (1024*1024):.2f} MB in {time.time()-t0:.1f}s. Decompressing and extracting bus stops...")
t1 = time.time()

# Decompress and process
decompressed_text = lzma.decompress(compressed_bytes).decode('utf-8', errors='ignore')
print(f"Decompressed to {len(decompressed_text) / (1024*1024):.2f} MB in {time.time()-t1:.1f}s. Parsing JSON...")

geojson = json.loads(decompressed_text)
features = geojson.get('features', [])
print(f"Total OSM features in NewDelhi extract: {len(features)}")

bus_stops = []
for f in features:
    props = f.get('properties', {})
    geom = f.get('geometry', {})
    # Check if bus stop, bus station, or platform
    hway = props.get('highway')
    amen = props.get('amenity')
    pub = props.get('public_transport')
    
    if hway == 'bus_stop' or amen == 'bus_station' or pub in ['platform', 'stop_position', 'station']:
        coords = geom.get('coordinates')
        if coords and len(coords) >= 2:
            lon, lat = coords[0], coords[1]
            name = props.get('name') or props.get('name:en') or props.get('description') or 'Unnamed'
            bus_stops.append({
                'name': name,
                'latitude': lat,
                'longitude': lon,
                'is_hub': amen == 'bus_station' or 'depot' in name.lower() or 'terminal' in name.lower() or 'isbt' in name.lower(),
                'osm_id': props.get('@id') or props.get('id'),
                'tags': {k: props[k] for k in ['highway', 'amenity', 'public_transport', 'shelter', 'operator'] if k in props}
            })

print(f"\nExtracted {len(bus_stops)} official OSM bus stops & stations from New Delhi map!")
hubs = [s for s in bus_stops if s['is_hub']]
local = [s for s in bus_stops if not s['is_hub']]
print(f"  Major Bus Stations / Terminals: {len(hubs)}")
print(f"  Regular Bus Stops: {len(local)}")

with open('data/osm_delhi_all_bus_stops.json', 'w', encoding='utf-8') as out:
    json.dump(bus_stops, out, indent=2)

print("Saved to data/osm_delhi_all_bus_stops.json!")

# Print first 15 stops
for s in bus_stops[:15]:
    print(f"  • {s['name']}: [{s['latitude']}, {s['longitude']}] (Hub: {s['is_hub']})")
