import json
import math
import os
import networkx as nx

# Load data
with open("data/processed/corridors_routed.json", "r", encoding="utf-8") as f:
    corridors = json.load(f)

with open("data/processed/stop_profiles.json", "r", encoding="utf-8") as f:
    stops_list = json.load(f)
stops_meta = {s['name']: s for s in stops_list}

with open("data/processed/transit_graph_edges.json", "r", encoding="utf-8") as f:
    edges = json.load(f)

graph = nx.DiGraph()
for s in stops_list:
    graph.add_node(s['name'], **s)
for e in edges:
    graph.add_edge(e['start_stop'], e['end_stop'], route=e['route'], frequency=e['frequency'])

def resolve_intermediate_stops(orig, dest, is_express=False):
    # 1. Search in corridors
    for c in corridors:
        c_stops = c.get('stops', [])
        # Find orig and dest in corridor
        idx_o = -1
        idx_d = -1
        for i, s in enumerate(c_stops):
            if orig.lower() in s.lower() or s.lower() in orig.lower():
                idx_o = i
            if dest.lower() in s.lower() or s.lower() in dest.lower():
                idx_d = i
        if idx_o != -1 and idx_d != -1 and idx_o != idx_d:
            step = 1 if idx_d > idx_o else -1
            segment = c_stops[idx_o:idx_d + step:step]
            intermediates = segment[1:-1]
            if is_express and len(intermediates) > 2:
                # Express stops: keep only major hub intermediate
                major_int = [s for s in intermediates if stops_meta.get(s, {}).get('is_major_hub')]
                if not major_int:
                    major_int = [intermediates[len(intermediates)//2]]
                return intermediates, major_int
            return intermediates, intermediates

    # 2. Search shortest path in transit graph
    try:
        path = nx.shortest_path(graph, orig, dest)
        if len(path) >= 3:
            intermediates = path[1:-1]
            if is_express and len(intermediates) > 2:
                major_int = [s for s in intermediates if stops_meta.get(s, {}).get('is_major_hub')]
                if not major_int:
                    major_int = [intermediates[len(intermediates)//2]]
                return intermediates, major_int
            return intermediates, intermediates
    except Exception:
        pass

    # 3. Geometric corridor projection between orig and dest
    o_info = stops_meta.get(orig)
    d_info = stops_meta.get(dest)
    if o_info and d_info:
        o_lat, o_lon = o_info['latitude'], o_info['longitude']
        d_lat, d_lon = d_info['latitude'], d_info['longitude']
        vec_lat = d_lat - o_lat
        vec_lon = d_lon - o_lon
        vec_len_sq = vec_lat**2 + vec_lon**2
        
        candidates = []
        for name, s in stops_meta.items():
            if name == orig or name == dest: continue
            lat, lon = s['latitude'], s['longitude']
            # projection scalar t in [0.1, 0.9]
            if vec_len_sq > 0:
                t = ((lat - o_lat)*vec_lat + (lon - o_lon)*vec_lon) / vec_len_sq
                if 0.1 <= t <= 0.9:
                    # perpendicular distance
                    proj_lat = o_lat + t * vec_lat
                    proj_lon = o_lon + t * vec_lon
                    dist = math.hypot((lat - proj_lat)*111000, (lon - proj_lon)*111000)
                    if dist < 2500: # within 2.5km of direct line
                        candidates.append((t, dist, name, s.get('is_major_hub', False)))
        candidates.sort(key=lambda x: x[0]) # sort in order of travel from orig to dest
        
        # Pick 3 to 6 sequential stops
        step = max(1, len(candidates) // 5)
        all_int = [c[2] for c in candidates[::step]][:5]
        major_int = [c[2] for c in candidates if c[3]][:2]
        if not major_int and all_int:
            major_int = [all_int[len(all_int)//2]]
        return all_int, major_int

    return [], []

# Test for several key routes:
pairs = [
    ("Saket Bus Stop", "Dhaula Kuan"),
    ("Shahdara", "Anand Vihar ISBT"),
    ("Kashmere Gate", "AIIMS"),
    ("Mehrauli", "Badarpur Border"),
    ("Munirka Village", "Nehru Place")
]

for o, d in pairs:
    all_stops, exp_stops = resolve_intermediate_stops(o, d, is_express=True)
    print(f"\nTrip: {o} -> {d}")
    print(f"  Regular All Intermediate ({len(all_stops)}):", all_stops)
    print(f"  Express Stops ({len(exp_stops)}):", exp_stops)
