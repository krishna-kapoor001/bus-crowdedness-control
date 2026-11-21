import json, sqlite3, math, re
from collections import defaultdict

conn = sqlite3.connect('data/flowpulse.db')
c = conn.cursor()
c.execute('SELECT id, name, latitude, longitude, corridor, monthly_boardings, monthly_alightings FROM stops WHERE is_major_hub = 1')
hubs_raw = c.fetchall()
conn.close()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlam/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def base_facility_name(name):
    # Normalize name to identify the facility
    clean = re.sub(r'\(.*?\)', '', name).strip()
    clean = re.sub(r'\b(terminal|depot|bus stand|isbt|crossing|cluster)\b', '', clean, flags=re.IGNORECASE)
    clean = re.sub(r'[-_/]', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean.lower()

# Check which hubs are within 500m of each other
clusters = []
used = set()

for i, h1 in enumerate(hubs_raw):
    if i in used: continue
    cl = [h1]
    used.add(i)
    for j in range(i+1, len(hubs_raw)):
        if j in used: continue
        h2 = hubs_raw[j]
        d = haversine(h1[2], h1[3], h2[2], h2[3])
        # If very close (< 450m) and similar facility
        if d <= 450:
            cl.append(h2)
            used.add(j)
    clusters.append(cl)

print(f"Total raw hub entries: {len(hubs_raw)}")
print(f"Unified major bus stands/hubs facilities: {len(clusters)}")

multi_hub_clusters = [cl for cl in clusters if len(cl) > 1]
print(f"Facilities with multiple duplicate hub dots: {len(multi_hub_clusters)}")
for cl in multi_hub_clusters:
    names = [h[1] for h in cl]
    print(f"  • Cluster: {names}")
