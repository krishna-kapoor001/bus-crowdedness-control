import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.app.config import settings

routed_file = os.path.join(settings.PROCESSED_DATA_DIR, 'corridors_routed.json')
print("PROCESSED_DATA_DIR:", settings.PROCESSED_DATA_DIR)
print("routed_file exists:", os.path.exists(routed_file))
if os.path.exists(routed_file):
    print("routed_file size:", os.path.getsize(routed_file))
