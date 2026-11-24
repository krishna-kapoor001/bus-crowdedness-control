import json
import sys
import os

sys.path.insert(0, os.path.abspath('.'))
from backend.app.services.journey_service import JourneyService

js = JourneyService()
res = js.plan_journey('Saket Bus Stop', 'Dhaula Kuan', '08:30')
print('Keys in response:', list(res.keys()))
alt = res['alternatives'][0]
print('Keys in alternative:', list(alt.keys()))
print('\nSample alt fields:')
for k, v in alt.items():
    if k not in ['route_coordinates']:
        print(f"  {k}: {v}")
