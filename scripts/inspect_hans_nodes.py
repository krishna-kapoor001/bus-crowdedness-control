import json

with open('data/osm_delhi_all_bus_stops.json', 'r', encoding='utf-8') as f:
    osm = json.load(f)

hans_nodes = []
for o in osm:
    if 'hansraj' in o.get('name', '').lower():
        hans_nodes.append(o)

print("Hansraj nodes in osm_delhi_all_bus_stops.json:")
for i, h in enumerate(hans_nodes):
    print(f"Node {i+1}: lat={h.get('latitude')}, lon={h.get('longitude')}, name={h.get('name')}, tags={h.get('tags')}")
