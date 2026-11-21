import xml.etree.ElementTree as ET

# Let's inspect the entire area around Shahdara from 28.670 to 28.678 and 77.282 to 77.292
# We have shahdara_osm_map.xml and shahdara_south_map.xml
# Let's check which ways have landuse, amenity, leisure, highway, etc.

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
        
        # Check green patch (leisure=park, landuse=grass, etc.)
        if any(tags.get(k) in ['park', 'grass', 'garden', 'greenfield'] for k in ['leisure', 'landuse']):
            print(f"GREEN PATCH in {fname}: Way {w.get('id')}, tags={tags}, center=({c_lat}, {c_lon})")
            
        # Check the long white strip with rounded end or traffic island
        if tags.get('traffic_calming') or tags.get('area') == 'yes' or 'platform' in str(tags):
            print(f"PLATFORM/ISLAND in {fname}: Way {w.get('id')}, tags={tags}, center=({c_lat}, {c_lon})")
