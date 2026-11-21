import json
import csv

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

for s in stops:
    if 'r.k.' in s['name'].lower() or 'rk puram' in s['name'].lower():
        print("stop_profile:", s)

with open('delhi_bus_stands_coordinates.csv', 'r', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        if 'r.k.' in row['bus_stand_name'].lower() or 'rk puram' in row['bus_stand_name'].lower():
            print("csv stand:", row)
