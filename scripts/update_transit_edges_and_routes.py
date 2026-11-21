import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')

METRO_REPLACEMENTS = {
    'Chhatarpur Metro Station': 'Chhatarpur Bus Stop',
    'Vishwa Vidyalaya Metro Station': 'Vishwa Vidyalaya Bus Stop',
    'Saket Metro Station': 'Saket Bus Stop',
    'Karol Bagh Metro Station': 'Karol Bagh Bus Stop',
    'Laxmi Nagar (Vikas Marg) / Laxmi Nagar Metro Station': 'Laxmi Nagar (Vikas Marg) Bus Stop',
    'Rajindera Place Metro Station': 'Rajendra Place Bus Stop',
    'Shadipur Dtc Colony Metro Station': 'Shadipur DTC Colony Bus Stop',
    'Saket A Block (Malviya Nagar Metro Station)': 'Saket A Block (Malviya Nagar Bus Stop)',
    'Karol Bagh Metro': 'Karol Bagh Bus Stand',
    'Saket Metro Sation / Said-Ul-Ajaib': 'Saket Said-Ul-Ajaib Bus Stop',
    'Jahangir Puri Metro Station': 'Jahangirpuri Bus Stop',
    'Rithala Metro Station': 'Rithala Bus Stop',
    'Shadi Pur Metro Station': 'Shadipur Bus Stop',
    'Dwarka More Metro Station': 'Dwarka Mor Bus Stand',
    'Lajpat Nagar Metro': 'Lajpat Nagar Bus Stand',
    'Chhatarpur Metro': 'Chhatarpur Bus Stand',
    'Punj Sons / Govind Puri Metro Station': 'Punj Sons / Govindpuri Bus Stop',
    'Andheria More / Chhatarpur Metro Station': 'Andheria Mor / Chhatarpur Bus Stop',
    'Jahangirpuri Metro Station Gt Road': 'Jahangirpuri GT Road Bus Stop',
    'Qutub Minar Metro Sation': 'Qutub Minar Bus Stop',
    'Metro Train Depot': 'Shastri Park Transit Depot',
    'Ip Depot Metro Station': 'IP Depot Bus Stand',
    'Shastri Park Metro Depot': 'Shastri Park Bus Depot'
}

# 1. Update transit_graph_edges.json
for p in [os.path.join(PROCESSED_DIR, 'transit_graph_edges.json'), os.path.join(DATA_DIR, 'transit_edges.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            edges = json.load(f)
        count = 0
        for e in edges:
            u = e['start_stop']
            v = e['end_stop']
            if u in METRO_REPLACEMENTS:
                e['start_stop'] = METRO_REPLACEMENTS[u]
                count += 1
            if v in METRO_REPLACEMENTS:
                e['end_stop'] = METRO_REPLACEMENTS[v]
                count += 1
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(edges, f, indent=2)
        print(f"Updated {p}: {count} edge replacements")

# 2. Update route_profiles.json & routes_meta.json
for p in [os.path.join(PROCESSED_DIR, 'route_profiles.json'), os.path.join(DATA_DIR, 'routes_meta.json')]:
    if os.path.exists(p):
        with open(p, 'r', encoding='utf-8') as f:
            routes = json.load(f)
        count = 0
        for r in routes:
            orig = r.get('origin', '')
            dest = r.get('destination', '')
            if orig in METRO_REPLACEMENTS:
                r['origin'] = METRO_REPLACEMENTS[orig]
                count += 1
            if dest in METRO_REPLACEMENTS:
                r['destination'] = METRO_REPLACEMENTS[dest]
                count += 1
        with open(p, 'w', encoding='utf-8') as f:
            json.dump(routes, f, indent=2)
        print(f"Updated {p}: {count} route origin/destination replacements")

print("All transit edges and route profiles updated!")
