import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.findall('node')}

for w in root.findall('way'):
    if w.get('id') == '370165976':
        print("Bhola Nath Nagar Marg nodes:")
        for nd in w.findall('nd'):
            ref = nd.get('ref')
            if ref in nodes:
                print(f"  {ref}: {nodes[ref]}")
