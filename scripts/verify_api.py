import urllib.request
import json

url = 'http://127.0.0.1:8000/api/v1/network/geojson'
try:
    with urllib.request.urlopen(url, timeout=10) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        features = data['features']
        print(f"API SUCCESS! Total stops returned: {len(features)}")
        hubs = [f for f in features if f['properties']['is_hub']]
        print(f"Total Major Bus Stands/Terminals (hubs): {len(hubs)}")
        print("\nSample 10 Bus Stands (Black Dots):")
        for h in hubs[:10]:
            coords = h['geometry']['coordinates']
            print(f"  {h['properties']['name']}: lat={coords[1]}, lon={coords[0]}")
        
        # Check RK Puram Sec 1
        rk = [f for f in features if 'r.k. puram' in f['properties']['name'].lower() or 'rk puram' in f['properties']['name'].lower()]
        print("\nRK Puram entries:")
        for r in rk:
            coords = r['geometry']['coordinates']
            print(f"  {r['properties']['name']}: is_hub={r['properties']['is_hub']}, coords=({coords[1]}, {coords[0]})")
except Exception as e:
    print("API Error:", e)
