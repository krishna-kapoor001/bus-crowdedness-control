import re

with open('data/NewDelhi.osm.csv', 'r', encoding='utf-8', errors='ignore') as f:
    count = 0
    for line in f:
        if 'bus_stop' in line or 'bus_station' in line or 'Yamuna Vihar' in line:
            print(line.strip()[:180])
            count += 1
            if count >= 15:
                break
