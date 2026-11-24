import json
import sqlite3

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

print(f"Stops count before merge: {len(stops)}")

merge_map = {
    # 18.5m duplicate in Najafgarh
    'Najafgarh Dhansa Stand': 'Najafgarh Terminal',
    # 35.2m duplicate on Najafgarh Road
    'Tagore Garden D Block': 'Rajouri Garden'
}

extra_b = {}
extra_a = {}
for s in stops:
    if s['name'] in merge_map:
        target = merge_map[s['name']]
        extra_b[target] = extra_b.get(target, 0) + s.get('monthly_boardings', 0)
        extra_a[target] = extra_a.get(target, 0) + s.get('monthly_alightings', 0)

filtered = []
for s in stops:
    if s['name'] in merge_map:
        continue
    if s['name'] in extra_b:
        s['monthly_boardings'] = s.get('monthly_boardings', 0) + extra_b[s['name']]
        s['monthly_alightings'] = s.get('monthly_alightings', 0) + extra_a[s['name']]
    filtered.append(s)

filtered.sort(key=lambda x: x['monthly_boardings'], reverse=True)
hubs_count = len([s for s in filtered if s.get('is_major_hub')])

print(f"Stops count after merge: {len(filtered)}, Major Bus Stands: {hubs_count}")

# Save JSON files
with open('data/processed/stop_profiles.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

with open('data/stops_meta.json', 'w', encoding='utf-8') as f:
    json.dump(filtered, f, indent=2, ensure_ascii=False)

# Sync Database
conn = sqlite3.connect("data/flowpulse.db")
cur = conn.cursor()
cur.execute("DELETE FROM stops;")
for idx, s in enumerate(filtered, 1):
    cur.execute("""
        INSERT INTO stops (id, name, latitude, longitude, corridor, monthly_boardings, monthly_alightings, is_major_hub)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        idx,
        s['name'],
        s['latitude'],
        s['longitude'],
        s.get('corridor', 'Delhi Transit Network'),
        s.get('monthly_boardings', 0),
        s.get('monthly_alightings', 0),
        1 if s.get('is_major_hub') else 0
    ))
conn.commit()
conn.close()

print(f"Successfully saved and synced data/flowpulse.db: {len(filtered)} stops, {hubs_count} hubs!")
