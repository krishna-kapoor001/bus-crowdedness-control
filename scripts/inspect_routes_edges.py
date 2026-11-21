import json

with open("data/processed/route_profiles.json", "r", encoding="utf-8") as f:
    rp = json.load(f)

print(f"Total routes in route_profiles.json: {len(rp)}")
sample_key = list(rp.keys())[0] if isinstance(rp, dict) else 0
sample_route = rp[sample_key]
print(f"Sample route ({sample_key}):", sample_route)

with open("data/processed/transit_graph_edges.json", "r", encoding="utf-8") as f:
    tge = json.load(f)
print(f"Total edges in transit_graph_edges.json: {len(tge)}")
print("Sample edge:", tge[0] if isinstance(tge, list) else list(tge.items())[:2])
