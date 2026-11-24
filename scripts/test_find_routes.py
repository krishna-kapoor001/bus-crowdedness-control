import json, sys, os
sys.path.insert(0, os.path.abspath('.'))
from backend.app.services.journey_service import journey_service

res = journey_service.find_routes('Saket Bus Stop', 'Dhaula Kuan', '08:30')
print(json.dumps(res.dict(), indent=2, default=str)[:2000])
