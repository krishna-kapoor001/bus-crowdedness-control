import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.findall('node')}

print("=== All ways in bbox ===")
for w in root.findall('way'):
    wid = w.get('id')
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    nd_refs = [nd.get('ref') for nd in w.findall('nd')]
    coords = [nodes[r] for r in nd_refs if r in nodes]
    if not coords:
        continue
    c_lat = sum(c[0] for c in coords)/len(coords)
    c_lon = sum(c[1] for c in coords)/len(coords)
    # Check if coords are in 28.6738 to 28.6748 and 77.2865 to 77.288
    if 28.6735 <= c_lat <= 28.675 and 77.286 <= c_lon <= 77.288:
        print(f"Way {wid} (c_lat={c_lat:.6f}, c_lon={c_lon:.6f}): tags={tags}")
