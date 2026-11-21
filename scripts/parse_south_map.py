import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_south_map.xml")
root = tree.getroot()

nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.findall('node')}

for w in root.findall('way'):
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    name = tags.get('name', '')
    railway = tags.get('railway', '')
    if 'Red' in name or railway:
        nd_refs = [nd.get('ref') for nd in w.findall('nd')]
        coords = [nodes[r] for r in nd_refs if r in nodes]
        c_lat = sum(c[0] for c in coords)/len(coords) if coords else 0
        c_lon = sum(c[1] for c in coords)/len(coords) if coords else 0
        print(f"Way {w.get('id')}: {name}, railway={railway}, center=({c_lat:.6f}, {c_lon:.6f})")
