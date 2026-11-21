import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon')), {t.get('k'): t.get('v') for t in n.findall('tag')}) for n in root.findall('node')}

print("=== All buildings / information / platforms in the XML ===")
for w in root.findall('way'):
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    nd_refs = [nd.get('ref') for nd in w.findall('nd')]
    coords = [nodes[r][:2] for r in nd_refs if r in nodes]
    if not coords:
        continue
    c_lat = sum(c[0] for c in coords) / len(coords)
    c_lon = sum(c[1] for c in coords) / len(coords)
    
    if any(k in tags for k in ['building', 'amenity', 'tourism', 'public_transport', 'highway']):
        if 28.6735 <= c_lat <= 28.676 and 77.285 <= c_lon <= 77.289:
            print(f"Way {w.get('id')}: {tags.get('name', '')} {tags.get('amenity', '')} {tags.get('tourism', '')} {tags.get('building', '')} {tags.get('highway', '')}")
            print(f"    Center: lat={c_lat:.7f}, lon={c_lon:.7f}")

# Also check relations!
for r in root.findall('relation'):
    tags = {t.get('k'): t.get('v') for t in r.findall('tag')}
    print(f"Relation {r.get('id')}: {tags}")
