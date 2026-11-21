import csv
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

stands = []
seen = set()

# Keywords that indicate an official bus stand / terminal / depot / ISBT
stand_patterns = [
    r'\bterminal\b',
    r'\b\(t\)\b',
    r'\bisbt\b',
    r'\bdepot\b',
    r'\bstand\b',
    r'\bbus stand\b',
]

for g in gtfs:
    try:
        lat = float(g['stop_lat'])
        lon = float(g['stop_lon'])
        name = g['stop_name'].strip()
        
        # Delhi NCT bounding box
        if not (28.38 <= lat <= 28.88 and 76.84 <= lon <= 77.38):
            continue
            
        is_stand = any(re.search(pat, name, re.IGNORECASE) for pat in stand_patterns)
        if is_stand:
            clean = re.sub(r'\s+', ' ', name).title()
            # Normalize common names
            norm_key = re.sub(r'[^a-z0-9]', '', clean.lower())
            if norm_key not in seen:
                seen.add(norm_key)
                # Determine category
                n_lower = clean.lower()
                if 'isbt' in n_lower or 'kashmere gate' in n_lower or 'sarai kale khan' in n_lower or 'anand vihar isbt' in n_lower:
                    cat = 'Inter-State Bus Terminal (ISBT)'
                elif 'depot' in n_lower:
                    cat = 'DTC Bus Depot & Terminal'
                elif 'terminal' in n_lower or '(t)' in n_lower:
                    cat = 'Major Bus Terminal'
                else:
                    cat = 'Bus Stand'
                
                stands.append({
                    'name': clean,
                    'lat': round(lat, 6),
                    'lon': round(lon, 6),
                    'category': cat
                })
    except:
        continue

print(f"Found {len(stands)} official Delhi bus stands/terminals/depots in GTFS.")
cat_counts = {}
for s in stands:
    cat_counts[s['category']] = cat_counts.get(s['category'], 0) + 1
for cat, count in cat_counts.items():
    print(f"  {cat}: {count}")

print("\nSample 20 Bus Stands:")
for s in stands[:20]:
    print(f"  [{s['category']}] {s['name']} -> ({s['lat']}, {s['lon']})")
