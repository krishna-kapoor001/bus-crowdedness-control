import sys, os
sys.path.insert(0, ".")
sys.path.insert(0, "backend")

from backend.app.services.journey_service import journey_service

o = journey_service._resolve_stop("Anand Vihar ISBT Main Road")
d = journey_service._resolve_stop("Shivaji Stadium")
print(f"Resolved: '{o}' -> '{d}'")

reg, exp = journey_service._resolve_corridor_stops(o, d, 13.0)
print("Exp stops:", [s[0] for s in exp])
print("Reg stops:", [s[0] for s in reg])
