import csv

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

name = "Anand Vihar"
low = name.lower()

print("Searching GTFS for exact 'anand vihar'...")
for g in gtfs:
    if 'anand vihar' in g['stop_name'].lower():
        print(f"  {g['stop_id']}: '{g['stop_name']}' -> ({g['stop_lat']}, {g['stop_lon']})")

print("\nWhy did it match Nityanand Marg?")
words = [w for w in low.split() if len(w) > 3]
print("Words:", words)
for g in gtfs:
    if all(w in g['stop_name'].lower() for w in words):
        print(f"  MATCH: '{g['stop_name']}' -> ({g['stop_lat']}, {g['stop_lon']})")
        break
