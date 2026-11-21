import csv

with open('data/gtfs_delhi_stops.txt', encoding='utf-8') as f:
    gtfs = [row['stop_name'] for row in csv.DictReader(f)]

queries = ['kalka', 'mayur', 'ali pur', 'pahar', 'madan', 'badli']
for q in queries:
    m = [name for name in gtfs if q in name.lower()]
    print(f"'{q}': {m[:5]}")
