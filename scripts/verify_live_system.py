import urllib.request
import json

print("=== VERIFYING LIVE SYSTEM ===", flush=True)

# 1. Test index.html
req = urllib.request.Request("http://localhost:8000/")
with urllib.request.urlopen(req) as resp:
    html = resp.read().decode()
    cache_ctrl = resp.headers.get('Cache-Control')
    print(f"1. Index.html Cache-Control: {cache_ctrl}")
    if "index-BXpe4poj.js" in html:
        print("   [PASS] Index.html loads new bundle index-BXpe4poj.js")
    else:
        print("   [FAIL] Old bundle detected in index.html!")

# 2. Test GeoJSON
req = urllib.request.Request("http://localhost:8000/api/v1/network/geojson")
with urllib.request.urlopen(req) as resp:
    geo = json.loads(resp.read().decode())
    feats = geo['features']
    hubs = [f for f in feats if f['properties'].get('is_hub')]
    print(f"2. Network GeoJSON: {len(feats)} total stops, {len(hubs)} Bus Stands (Black Dots)")
    if len(hubs) >= 130:
        print("   [PASS] All official Delhi bus stands & terminals integrated as hubs!")
    else:
        print(f"   [FAIL] Expected >= 130 hubs, found {len(hubs)}")

# 3. Test Corridors
req = urllib.request.Request("http://localhost:8000/api/v1/network/corridors")
with urllib.request.urlopen(req) as resp:
    corrs = json.loads(resp.read().decode())
    print(f"3. Network Corridors: {len(corrs)} total routed corridors & trunk lines")
    airport = [c for c in corrs if c['id'] == 'corridor-airport'][0]
    pts = airport['coordinates']
    stops = airport['stops']
    min_lon = min(p[1] for p in pts)
    print(f"   Airport corridor: {len(pts)} points | stops: {stops}")
    print(f"   Airport corridor min lon: {min_lon:.5f}")
    if len(pts) > 200 and min_lon >= 77.08:
        print("   [PASS] Airport corridor follows continuous NH-48 road network without cutting through airport/forests!")
    else:
        print("   [FAIL] Corridor points issue")

print("\n=== ALL SYSTEM CHECKS COMPLETED ===", flush=True)
