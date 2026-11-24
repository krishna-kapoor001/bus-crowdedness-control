import urllib.request
import json
import time

time.sleep(1)

# 1. Test empty query (all 827 stops)
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops') as r:
    stops = json.loads(r.read().decode())
    hubs = [s for s in stops if s.get('is_major_hub')]
    print(f"Total stops in catalog: {len(stops)}, Major Bus Stands: {len(hubs)}")

# 2. Test 'bus stand' query
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops?query=bus+stand') as r:
    bus_stands = json.loads(r.read().decode())
    print(f"Query 'bus stand' matches: {len(bus_stands)} stops")
    print("Top 5 bus stand matches:", [s['name'] for s in bus_stands[:5]])

# 3. Test 'Hansraj' query
with urllib.request.urlopen('http://localhost:8000/api/v1/journey/stops?query=hansraj') as r:
    hansraj = json.loads(r.read().decode())
    print(f"Query 'hansraj' matches: {len(hansraj)} stops: {[s['name'] for s in hansraj]}")
