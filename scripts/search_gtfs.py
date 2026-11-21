import csv
import sys
import re

with open('data/gtfs_delhi_stops.txt', 'r', encoding='utf-8') as f:
    gtfs = list(csv.DictReader(f))

def search(query):
    print(f"=== SEARCH: '{query}' ===")
    q_re = re.compile(query, re.IGNORECASE)
    count = 0
    for g in gtfs:
        if q_re.search(g['stop_name']):
            print(f"  {g['stop_id']}: '{g['stop_name']}' -> ({g['stop_lat']}, {g['stop_lon']})")
            count += 1
            if count >= 10:
                print("  ... more matches omitted")
                break
    if count == 0:
        print("  NO MATCHES")

queries = [
    'adhchini', 'alipur', 'ambedkar', 'badli', 'kashm', 'safdar', 'r.*k.*puram',
    'gtk', 'janakpuri', 'dabri', 'laxmi', 'madangir', 'shakarpur', 'sarai roh',
    'saidul', 'saket', 'pul pr', 'vayusena', 'zakir', 'connaught', 'shivaji',
    'qutab', 'punj', 'mahipal', 'reddi', 'nangloi', 'uttam'
]

for q in queries:
    search(q)
