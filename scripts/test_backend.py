import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

print("1. Testing /health ...")
r = client.get('/health')
assert r.status_code == 200, f"Health check failed: {r.status_code}"
print("   Response:", r.json())

print("\n2. Testing /api/v1/overview ...")
r = client.get('/api/v1/overview')
assert r.status_code == 200, f"Overview failed: {r.status_code}"
kpis = r.json()['kpis']
print(f"   KPIs: Demand={kpis['estimated_passenger_demand']:,}, Routes={kpis['analyzed_transport_routes']}, Confidence={kpis['model_prediction_confidence']}%")

print("\n3. Testing /api/v1/journey/plan ...")
r = client.post('/api/v1/journey/plan', json={
    'origin': 'Saket Metro Station',
    'destination': 'Dhaula Kuan',
    'departure_time': '08:30',
    'prefer_less_crowded': True
})
assert r.status_code == 200, f"Journey plan failed: {r.status_code}"
data = r.json()
print(f"   Origin: {data['origin']} -> Dest: {data['destination']}")
print(f"   Alternatives found: {len(data['alternatives'])}")
for alt in data['alternatives']:
    print(f"   - [{alt['badge']}] Routes: {alt['bus_routes']}, Duration: {alt['total_duration_mins']} mins, Crowd: {alt['crowd_level']} (Score: {alt['crowd_score']}/100, Confidence: {alt['prediction_confidence']}%)")

print("\n4. Testing /api/v1/simulation/shift ...")
r = client.post('/api/v1/simulation/shift', json={
    'demand_multiplier': 1.25,
    'peak_shift_factor': -0.15
})
assert r.status_code == 200, f"Simulation failed: {r.status_code}"
sim = r.json()
print(f"   System Wide Delta: {sim['system_wide_delta_pct']}% across {len(sim['corridors'])} corridors")
print(f"   Corridor 1: {sim['corridors'][0]['corridor_name']} => {sim['corridors'][0]['delta_pct']}% ({sim['corridors'][0]['simulated_crowd_level']})")

print("\n5. Testing /api/v1/models/info ...")
r = client.get('/api/v1/models/info')
assert r.status_code == 200, f"Models info failed: {r.status_code}"
m = r.json()
print(f"   Model: {m['model_name']} | Split: {m['dataset_split']}")
print(f"   Test MAE: {m['mae']} pax/hr | Baseline MAE: {m['baseline_mae']} pax/hr | R2: {m['r2_score']}")

print("\n6. Testing /api/v1/analytics/hourly ...")
r = client.get('/api/v1/analytics/hourly')
assert r.status_code == 200, f"Hourly analytics failed: {r.status_code}"
print(f"   Retrieved {len(r.json())} hourly data points")

print("\n7. Testing /api/v1/network/geojson ...")
r = client.get('/api/v1/network/geojson')
assert r.status_code == 200, f"Network geojson failed: {r.status_code}"
print(f"   Retrieved {len(r.json()['features'])} geo features")

print("\nALL BACKEND API TESTS PASSED SUCCESSFULLY!")
