import json

with open('data/processed/stop_profiles.json', 'r', encoding='utf-8') as f:
    stops = json.load(f)

with open('data/processed/route_profiles.json', 'r', encoding='utf-8') as f:
    routes = json.load(f)

# Check route 522UP and 546DOWN
for r in routes:
    if r.get('route_id') in ['522UP', '546DOWN']:
        print(f"Route {r.get('route_id')}: {r.get('route_name')}")
        print(f"  Stops: {r.get('stops')[:6]} ... {r.get('stops')[-4:]}")
