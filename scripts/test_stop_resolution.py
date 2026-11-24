import json, math, os, sys

sys.path.insert(0, os.path.abspath('.'))
from backend.app.services.journey_service import journey_service

with open('data/stops_meta.json', 'r', encoding='utf-8') as f:
    stops_meta = {s['name']: s for s in json.load(f)}

test_queries = [
    ("Saket", "Dhaula Kuan"),
    ("Kashmere Gate", "AIIMS"),
    ("Anand Vihar", "Shivaji Stadium"),
    ("Janakpuri", "Connaught Place"),
    ("Rohini", "Azadpur"),
    ("Badarpur", "Nehru Place"),
    ("Dwarka", "Uttam Nagar")
]

for o_query, d_query in test_queries:
    o_name = journey_service._resolve_stop(o_query)
    d_name = journey_service._resolve_stop(d_query)
    print(f"Query: '{o_query}' -> '{d_query}' | Resolved: '{o_name}' -> '{d_name}'")
