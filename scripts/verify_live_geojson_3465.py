import urllib.request
import json

url = "http://127.0.0.1:8000/api/v1/network/geojson"
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        features = data.get('features', [])
        print(f"GeoJSON feature count: {len(features)}")
        hubs = [f for f in features if f['properties'].get('is_hub')]
        locals = [f for f in features if not f['properties'].get('is_hub')]
        print(f"  Major Bus Stands / Terminals (Black dots): {len(hubs)}")
        print(f"  Regular Bus Stops (Blue dots): {len(locals)}")
        
        # Verify Shahdara Terminal is still on its exact OSM tile coordinates
        shahdara = [f for f in features if 'Shahdara' in f['properties']['name']]
        print(f"Shahdara stops found: {len(shahdara)}")
        for s in shahdara[:3]:
            print("  ", s['properties']['name'], "->", s['geometry']['coordinates'])
except Exception as e:
    print("Error:", e)
