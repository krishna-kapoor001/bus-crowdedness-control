import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {}
for n in root.findall('node'):
    nid = n.get('id')
    nodes[nid] = (float(n.get('lat')), float(n.get('lon')))

for w in root.findall('way'):
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    name = tags.get('name', '')
    railway = tags.get('railway', '')
    if 'Red Line' in name or railway:
        nd_refs = [nd.get('ref') for nd in w.findall('nd')]
        coords = [nodes[r] for r in nd_refs if r in nodes]
        print(f"RAILWAY/METRO WAY {w.get('id')}: {name}, railway={railway}")
        for lat, lon in coords:
            if 77.286 <= lon <= 77.288:
                print(f"   at lon {lon:.6f} -> lat {lat:.6f}")
