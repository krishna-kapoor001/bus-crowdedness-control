import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {}
for n in root.findall('node'):
    nid = n.get('id')
    lat = float(n.get('lat'))
    lon = float(n.get('lon'))
    tags = {t.get('k'): t.get('v') for t in n.findall('tag')}
    nodes[nid] = {'lat': lat, 'lon': lon, 'tags': tags}

print(f"Total nodes: {len(nodes)}")

# Find tagged nodes
for nid, n in nodes.items():
    if n['tags']:
        name = n['tags'].get('name', '')
        amenity = n['tags'].get('amenity', '')
        hw = n['tags'].get('highway', '')
        if 'Shahdara' in name or 'bus' in amenity or 'bus' in hw or 'bus' in name.lower() or 'terminal' in name.lower():
            print(f"TAGGED NODE {nid}: {n['tags']} at lat={n['lat']}, lon={n['lon']}")

# Find ways
for w in root.findall('way'):
    wid = w.get('id')
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    name = tags.get('name', '')
    amenity = tags.get('amenity', '')
    hw = tags.get('highway', '')
    if 'Shahdara' in name or 'bus' in amenity or 'bus' in hw or 'terminal' in name.lower():
        nd_refs = [nd.get('ref') for nd in w.findall('nd')]
        nd_coords = [nodes[ref] for ref in nd_refs if ref in nodes]
        if nd_coords:
            c_lat = sum(c['lat'] for c in nd_coords) / len(nd_coords)
            c_lon = sum(c['lon'] for c in nd_coords) / len(nd_coords)
            print(f"TAGGED WAY {wid}: {tags}")
            print(f"   Center: lat={c_lat:.6f}, lon={c_lon:.6f}")
            for ref in nd_refs:
                if ref in nodes:
                    print(f"     node {ref}: lat={nodes[ref]['lat']}, lon={nodes[ref]['lon']}")
