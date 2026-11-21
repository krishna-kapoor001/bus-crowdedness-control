import urllib.request
import json

# Check the live API
url = "http://localhost:8000/api/v1/network/geojson"
try:
    with urllib.request.urlopen(url, timeout=5) as resp:
        data = json.loads(resp.read().decode('utf-8'))
        for f in data.get('features', []):
            name = f.get('properties', {}).get('name', '')
            if 'Shahdara' in name:
                print("API Feature:", name, f.get('geometry'))
except Exception as e:
    print("API Error:", e)

# Also check frontend code: where does frontend get the dots?
# Does frontend load from /api/v1/network/geojson or from a static json in frontend/src/ or public/?
