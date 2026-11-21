import json, math

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

close_pairs = []
for i in range(len(stops)):
    s1 = stops[i]
    for j in range(i+1, len(stops)):
        s2 = stops[j]
        d = haversine(s1['latitude'], s1['longitude'], s2['latitude'], s2['longitude'])
        if d < 30:
            close_pairs.append((s1['name'], s2['name'], d))

print(f"Total pairs within 30m across all {len(stops)} stops: {len(close_pairs)}")
for c in close_pairs[:10]:
    print(c)

print('\nCheck Yamuna Vihar stops:')
for s in stops:
    if 'yamuna vihar' in s['name'].lower():
        print(f"  - {s['name']}: [{s['latitude']}, {s['longitude']}] (Hub: {s['is_major_hub']})")

print('\nCheck Shahdara stops:')
for s in stops:
    if 'shahdara' in s['name'].lower():
        print(f"  - {s['name']}: [{s['latitude']}, {s['longitude']}] (Hub: {s['is_major_hub']})")
