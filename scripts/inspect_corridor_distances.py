import json, math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

with open("data/corridors_routed.json", "r", encoding="utf-8") as f:
    corr = json.load(f)

for item in corr:
    cid = item.get('id')
    pts = item.get('coordinates', [])
    dist = sum(haversine(pts[i][0], pts[i][1], pts[i+1][0], pts[i+1][1]) for i in range(len(pts)-1)) if len(pts) > 1 else 0
    print(f"{cid:<25} | Name: {item.get('name')[:40]:<40} | Street Dist: {dist:.2f} km | Stops: {item.get('stops', [])}")
