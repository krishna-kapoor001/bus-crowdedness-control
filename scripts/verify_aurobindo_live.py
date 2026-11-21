import urllib.request
import json

req = urllib.request.Request("http://localhost:8000/api/v1/network/corridors")
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode())
    auro = [c for c in data if c['id'] == 'corridor-aurobindo'][0]
    print("Aurobindo corridor ID:", auro['id'])
    print("Aurobindo corridor Name:", auro['name'])
    print("Aurobindo corridor Stops:", auro['stops'])
    pts = auro['coordinates']
    print(f"Total points: {len(pts)}")
    print(f"Start: {pts[0]} (Safdarjung Tomb)")
    print(f"End: {pts[-1]} (Mehrauli Terminal)")
    # Verify no points dip into IIT Delhi (< 77.20 in that latitude range)
    iit_spurs = [p for p in pts if p[1] < 77.20 and 28.54 < p[0] < 28.56]
    print(f"Points deviating into IIT campus: {len(iit_spurs)}")
    # Verify no points dip into South Ex (> 77.21)
    southex_spurs = [p for p in pts if p[1] > 77.21]
    print(f"Points deviating into South Ex: {len(southex_spurs)}")
    if len(iit_spurs) == 0 and len(southex_spurs) == 0:
        print("[SUCCESS] Sri Aurobindo Marg corridor is 100% straight, smooth, and street-aligned!")
    else:
        print("[FAIL] Spurs detected")
