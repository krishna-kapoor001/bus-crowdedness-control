import json

# Check the backup or let's inspect the original 428 stops
# We can find them in git or in a script or in data/delhi_bus_stands_coordinates.csv before our edit
# Wait! In scripts/perfect_street_snapping_all_428.py, OSM_AUTHORITATIVE has all key hubs!
import re

from scripts.perfect_street_snapping_all_428 import OSM_AUTHORITATIVE

print(f"OSM Authoritative hubs: {len(OSM_AUTHORITATIVE)}")
for k, v in list(OSM_AUTHORITATIVE.items())[:10]:
    print(f"  {k}: {v}")
