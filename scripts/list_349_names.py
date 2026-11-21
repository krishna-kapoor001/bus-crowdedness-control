import json

with open('data/all_stop_names.txt', 'r', encoding='utf-8') as f:
    stops = [s.strip() for s in f if s.strip()]

for i, s in enumerate(sorted(stops)):
    print(f"{i+1:3d}. {s}")
