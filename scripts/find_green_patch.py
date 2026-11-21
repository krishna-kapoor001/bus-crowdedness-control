import xml.etree.ElementTree as ET

for fname in ["scripts/shahdara_osm_map.xml", "scripts/shahdara_south_map.xml"]:
    tree = ET.parse(fname)
    root = tree.getroot()
    nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.findall('node')}
    
    for w in root.findall('way'):
        tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
        nd_refs = [nd.get('ref') for nd in w.findall('nd')]
        coords = [nodes[r] for r in nd_refs if r in nodes]
        if not coords: continue
        c_lat = sum(c[0] for c in coords)/len(coords)
        c_lon = sum(c[1] for c in coords)/len(coords)
        
        # Check all tags
        for k, v in tags.items():
            if any(term in str(v).lower() for term in ['grass', 'park', 'garden', 'green', 'tree', 'pitch']):
                print(f"GREEN in {fname}: Way {w.get('id')} ({k}={v}), center=({c_lat:.6f}, {c_lon:.6f})")
                for r in nd_refs:
                    if r in nodes:
                        print(f"   node: {nodes[r]}")
