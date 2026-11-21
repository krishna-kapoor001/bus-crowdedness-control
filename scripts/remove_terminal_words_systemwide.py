import os
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

def clean_term(text):
    if not isinstance(text, str):
        return text
    n = re.sub(r'\s*\(\s*terminals?\s*\)\s*', ' ', text, flags=re.IGNORECASE)
    n = re.sub(r'\bterminal\s+2\b', 'T2', n, flags=re.IGNORECASE)
    n = re.sub(r'\s*\b(bus\s+)?terminals?\b\s*', ' ', n, flags=re.IGNORECASE)
    n = re.sub(r'\(\s*\)', '', n)
    n = re.sub(r'\(\s*(.*?)\s*\)', r'(\1)', n)
    n = re.sub(r'\s*/\s*$', '', n)
    n = re.sub(r'^\s*/\s*', '', n)
    n = re.sub(r'\s+', ' ', n).strip()
    return n

# 1. Update corridors_routed.json
print("1. Updating corridors_routed.json...")
for p in [os.path.join(PROCESSED_DIR, 'corridors_routed.json'), os.path.join(DATA_DIR, 'corridors_routed.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            corridors = json.load(f)
        for c in corridors:
            c['name'] = clean_term(c['name'])
            c['stops'] = [clean_term(s) for s in c['stops']]
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(corridors, f, indent=2)
        print(f"   Updated {p}")

# 2. Update stop_profiles.json and stops_meta.json
print("2. Updating stop profiles...")
stop_rename_map = {}
for p in [os.path.join(PROCESSED_DIR, 'stop_profiles.json'), os.path.join(DATA_DIR, 'stops_meta.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            stops = json.load(f)
        for s in stops:
            old_name = s['name']
            new_name = clean_term(old_name)
            if old_name != new_name:
                stop_rename_map[old_name] = new_name
            s['name'] = new_name
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(stops, f, indent=2)
        print(f"   Updated {p} ({len(stop_rename_map)} stops renamed)")

# 3. Update route_profiles.json and routes_meta.json
print("3. Updating route profiles...")
for p in [os.path.join(PROCESSED_DIR, 'route_profiles.json'), os.path.join(DATA_DIR, 'routes_meta.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            routes = json.load(f)
        for r in routes:
            if 'origin' in r:
                r['origin'] = clean_term(r['origin'])
            if 'destination' in r:
                r['destination'] = clean_term(r['destination'])
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(routes, f, indent=2)
        print(f"   Updated {p}")

# 4. Update transit_graph_edges.json and transit_edges.json
print("4. Updating transit graph edges...")
for p in [os.path.join(PROCESSED_DIR, 'transit_graph_edges.json'), os.path.join(DATA_DIR, 'transit_edges.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            edges = json.load(f)
        for e in edges:
            if 'start_stop' in e:
                e['start_stop'] = clean_term(e['start_stop'])
            if 'end_stop' in e:
                e['end_stop'] = clean_term(e['end_stop'])
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(edges, f, indent=2)
        print(f"   Updated {p}")

# 5. Clean backend/app/routers/network.py
print("5. Updating backend/app/routers/network.py...")
net_py = os.path.join(BASE_DIR, 'backend', 'app', 'routers', 'network.py')
with open(net_py, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any occurrence of Terminal in names
for old_name, new_name in stop_rename_map.items():
    content = content.replace(f'"{old_name}"', f'"{new_name}"')
    content = content.replace(f"'{old_name}'", f"'{new_name}'")

content = re.sub(r' Terminal\b', '', content)
content = re.sub(r'\bTerminal\b', '', content)

with open(net_py, 'w', encoding='utf-8') as f:
    f.write(content)
print("   Updated network.py")

print("\n✓ SUCCESS: 'Terminal' words removed system-wide across all stops, routes, corridors, and graphs!")
