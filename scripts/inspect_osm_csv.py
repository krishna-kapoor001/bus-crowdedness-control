import csv

with open('data/NewDelhi.osm.csv', 'r', encoding='utf-8', errors='ignore') as f:
    for i in range(25):
        line = f.readline()
        print(f"Line {i}: {line.strip().split('\t')}")
