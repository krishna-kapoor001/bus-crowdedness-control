import re

stops_found = []
with open('data/NewDelhi.osm.csv', 'r', encoding='utf-8', errors='ignore') as f:
    for line in f:
        # Check node entries
        parts = line.strip().split('\t')
        if len(parts) >= 3 and parts[0] == 'node':
            # Check if name looks like a bus stop or area
            name = parts[2]
            # In OSM CSV, some rows have additional tags or categories in parts[3]
            cat = parts[3] if len(parts) > 3 else ''
            stops_found.append((parts[1], name, cat))

print(f"Total named nodes in NewDelhi.osm.csv: {len(stops_found)}")
bus_nodes = [s for s in stops_found if any(t in s[1].lower() or t in s[2].lower() for t in ['bus', 'stop', 'stand', 'depot', 'terminal'])]
print(f"Nodes with bus/stop/stand/depot/terminal: {len(bus_nodes)}")
for b in bus_nodes[:20]:
    print(f"  ID: {b[0]} | Name: '{b[1]}' | Cat: '{b[2]}'")
