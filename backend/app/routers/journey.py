import os
import json
import re
from fastapi import APIRouter, Query, Response
from fastapi.responses import JSONResponse
from backend.app.config import settings
from backend.app.services.journey_service import journey_service
from backend.app.schemas.schemas import JourneySearchRequest, JourneySearchResponse

router = APIRouter()

# In-memory pre-warmed stops and routes caches for high concurrency
CACHED_STOPS = []
CACHED_ROUTES = []

def _init_in_memory_catalog():
    global CACHED_STOPS, CACHED_ROUTES
    stops_file = os.path.join(settings.PROCESSED_DATA_DIR, 'stop_profiles.json')
    if not os.path.exists(stops_file):
        stops_file = os.path.join(settings.DATA_DIR, 'stops_meta.json')
    if os.path.exists(stops_file):
        with open(stops_file, 'r') as f:
            raw_stops = json.load(f)
            CACHED_STOPS = [
                {
                    "id": idx + 1,
                    "name": s.get('name'),
                    "latitude": s.get('latitude'),
                    "longitude": s.get('longitude'),
                    "corridor": s.get('corridor'),
                    "is_major_hub": s.get('is_major_hub', False),
                    "monthly_boardings": s.get('monthly_boardings', 0)
                }
                for idx, s in enumerate(raw_stops)
            ]
            CACHED_STOPS.sort(key=lambda x: x['monthly_boardings'], reverse=True)

    routes_file = os.path.join(settings.PROCESSED_DATA_DIR, 'route_profiles.json')
    if not os.path.exists(routes_file):
        routes_file = os.path.join(settings.DATA_DIR, 'routes_meta.json')
    if os.path.exists(routes_file):
        with open(routes_file, 'r') as f:
            raw_routes = json.load(f)
            CACHED_ROUTES = [
                {
                    "route_id": r.get('route_id'),
                    "direction": r.get('direction', 'UP'),
                    "origin": r.get('origin', 'Bus Stand'),
                    "destination": r.get('destination', 'Destination Hub'),
                    "total_tickets": r.get('total_tickets', 0),
                    "avg_daily_passengers": r.get('avg_daily_passengers', 0.0),
                    "is_ac": r.get('is_predominantly_ac', False)
                }
                for r in raw_routes[:200]
            ]

_init_in_memory_catalog()

@router.post("/plan", response_model=JourneySearchResponse)
def plan_journey(req: JourneySearchRequest):
    return journey_service.find_routes(
        origin=req.origin,
        destination=req.destination,
        departure_time=req.departure_time or "08:30",
        prefer_less_crowded=req.prefer_less_crowded or False,
        day_type=req.day_type or "weekday"
    )

@router.get("/stops")
def list_stops(query: str = Query(None)):
    """Ultra-fast in-memory stop search across all 757 verified stops."""
    if not query:
        return JSONResponse(
            content=CACHED_STOPS,
            headers={"Cache-Control": "public, max-age=3600"}
        )
    q_low = query.strip().lower()
    is_bus_stand_query = any(k in q_low for k in ['bus stand', 'stand', 'busstand', 'bus-stand', 'bus stands', 'terminal', 'terminals', 'hub', 'hubs'])
    
    matches = [
        s for s in CACHED_STOPS 
        if (is_bus_stand_query and s.get('is_major_hub')) or
           q_low in s['name'].lower() or 
           (s.get('corridor') and q_low in s['corridor'].lower())
    ]
    # Prioritize major bus stands at top of search results
    matches.sort(key=lambda s: (not s.get('is_major_hub', False), -s.get('monthly_boardings', 0)))
    return JSONResponse(
        content=matches[:200],
        headers={"Cache-Control": "public, max-age=3600"}
    )

@router.get("/routes")
def list_routes():
    """Zero-DB in-memory route directory."""
    return JSONResponse(
        content=CACHED_ROUTES[:150],
        headers={"Cache-Control": "public, max-age=3600"}
    )
