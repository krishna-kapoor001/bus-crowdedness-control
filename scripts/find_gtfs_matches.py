import json
import csv
import re

with open("data/gtfs_delhi_stops.txt", "r", encoding="utf-8") as f:
    gtfs = list(csv.DictReader(f))

candidates = [
    "Saket Bus Stop",
    "Sheikh Sarai Phase Ii / Shaheed Bhagat Singh College",
    "Maya Puri Depot",
    "Alipur Gt Road",
    "Devoli Road Crossing",
    "Khanpur Extension / Devli Road Xing / Dakshin Puri G-Block",
    "Pul Prehladpur (Badarpur)",
    "Prem Nursary",
    "Air Traffic Control Office",
    "Kalindi Kunj Border",
    "Dada Dev Mandir",
    "Qamruddin Nagar",
    "Old Delhi Railway Station",
    "Vayusenabad (Tigri)",
    "Nizamuddin Railway Station",
    "Chhatarpur Extension",
    "Alipur Village",
    "Narela",
    "Prehlad Pur",
    "Vasant Kunj Sec A Pkt B/C / Vasant Vihar Bpc",
    "Shastri Park Bus Depot"
]

for cand in candidates:
    print(f"=== Candidate: {cand} ===")
    tokens = [t for t in re.sub(r'[^a-z0-9]', ' ', cand.lower()).split() if len(t) > 2 and t not in ['bus', 'stop', 'stand', 'station']]
    matches = []
    for g in gtfs:
        g_name = g['stop_name'].lower()
        score = sum(1 for t in tokens if t in g_name)
        if score >= 1:
            matches.append((score, g['stop_name'], g['stop_lat'], g['stop_lon']))
    matches.sort(key=lambda x: x[0], reverse=True)
    for m in matches[:4]:
        print(f"   Match (score {m[0]}): {m[1]} -> ({m[2]}, {m[3]})")
