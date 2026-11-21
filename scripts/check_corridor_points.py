import json

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

# Corridors:
# 1. DND Flyway: Lat 28.57 - 28.585, Lon 77.265 - 77.315
dnd = [s for s in stops if 28.57 <= s['latitude'] <= 28.585 and 77.265 <= s['longitude'] <= 77.315]
print("DND corridor stops:", len(dnd), [s['name'] for s in dnd])

# 2. Barapullah Flyover: Lat 28.58 - 28.59, Lon 77.22 - 77.26
bp = [s for s in stops if 28.58 <= s['latitude'] <= 28.59 and 77.23 <= s['longitude'] <= 77.255]
print("Barapullah corridor stops:", len(bp), [s['name'] for s in bp])

# 3. NH-48 Expressway: from Dhaula Kuan (28.59, 77.16) to Rajokri Border (28.51, 77.09)
nh48 = [s for s in stops if 28.51 <= s['latitude'] <= 28.58 and 77.08 <= s['longitude'] <= 77.16 and any(k in s['name'].lower() for k in ['shiv murti', 'mahipal', 'rangpuri', 'centaur', 'samalka', 'rajokari', 'nh'])]
print("\nNH-48 highway stops:", len(nh48))
for s in nh48:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")

# 4. Delhi-Meerut Expressway (NH-24/NH-9): Lat 28.61 - 28.64, Lon 77.27 - 77.34
dme = [s for s in stops if 28.61 <= s['latitude'] <= 28.64 and 77.27 <= s['longitude'] <= 77.34 and any(k in s['name'].lower() for k in ['nhw', 'national highway', 'bypass', 'pusta', 'samaspur', 'khichdipur', 'trilokpuri', 'gazipur'])]
print("\nNH-9/DME corridor stops:", len(dme))
for s in dme:
    print(f"  {s['name']}: ({s['latitude']}, {s['longitude']})")
