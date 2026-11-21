import xml.etree.ElementTree as ET

tree = ET.parse("scripts/shahdara_osm_map.xml")
root = tree.getroot()

nodes = {n.get('id'): (float(n.get('lat')), float(n.get('lon'))) for n in root.findall('node')}

def get_center(w):
    nd_refs = [nd.get('ref') for nd in w.findall('nd')]
    coords = [nodes[r] for r in nd_refs if r in nodes]
    if coords:
        return sum(c[0] for c in coords)/len(coords), sum(c[1] for c in coords)/len(coords)
    return None

w_info = next(w for w in root.findall('way') if w.get('id') == '351420747')
w_bldg = next(w for w in root.findall('way') if w.get('id') == '351420833')
w_wall = next(w for w in root.findall('way') if w.get('id') == '683662846')

print("Information building (351420747):", get_center(w_info))
print("Adjacent building (351420833):", get_center(w_bldg))
print("Wall (683662846):", get_center(w_wall))

# What element renders "Shahdara Terminal" in OSM?
# In OSM standard style, amenity=bus_station or public_transport=station on a relation or way or node renders the bus icon and label!
# Which element has amenity=bus_station and name='Shahdara Terminal'?
for el in root.findall('.//*[@k="amenity"][@v="bus_station"]/..'):
    tags = {t.get('k'): t.get('v') for t in el.findall('tag')}
    print("amenity=bus_station element:", el.tag, el.get('id'), tags)
