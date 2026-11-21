import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

for w in root.findall('way'):
    tags = {t.get('k'): t.get('v') for t in w.findall('tag')}
    # print any tag containing "Red Line" or "Bhola Nath"
    for k, v in tags.items():
        if 'Bhola Nath' in v or 'Red Line' in v or 'Railway' in v or 'railway' in k:
            print(f"Way {w.get('id')}: {tags}")
