from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from backend.app.database import get_db
from backend.app.models.entities import Route, Stop, HourlyDemand

router = APIRouter()

@router.get("/hourly")
def get_hourly_analytics(
    db: Session = Depends(get_db),
    route: str = Query(None),
    corridor: str = Query(None)
):
    # Retrieve hourly aggregation from database
    q = db.query(
        HourlyDemand.hour,
        HourlyDemand.is_weekend,
        func.sum(HourlyDemand.passengers).label("total_passengers"),
        func.sum(HourlyDemand.tickets).label("total_tickets")
    )
    if route and route != "ALL":
        q = q.filter(HourlyDemand.route_id == route)

    rows = q.group_by(HourlyDemand.hour, HourlyDemand.is_weekend).order_by(HourlyDemand.hour).all()

    # Organize by hour: weekday vs weekend
    hourly_map = {h: {"hour": h, "time_label": f"{h:02d}:00", "weekday": 0, "weekend": 0} for h in range(24)}
    for r in rows:
        h = r.hour
        if 0 <= h < 24:
            if r.is_weekend == 1:
                hourly_map[h]["weekend"] += int(r.total_passengers or 0)
            else:
                hourly_map[h]["weekday"] += int(r.total_passengers or 0)

    return list(hourly_map.values())

@router.get("/routes")
def get_route_analytics(
    db: Session = Depends(get_db),
    sort_by: str = Query("passengers"),
    limit: int = Query(25)
):
    q = db.query(Route)
    if sort_by == "revenue":
        q = q.order_by(Route.total_revenue.desc())
    elif sort_by == "tickets":
        q = q.order_by(Route.total_tickets.desc())
    else:
        q = q.order_by(Route.total_passengers.desc())

    routes = q.limit(limit).all()
    return [
        {
            "route_id": r.route_id,
            "direction": r.direction,
            "origin": r.origin,
            "destination": r.destination,
            "total_tickets": r.total_tickets,
            "total_passengers": r.total_passengers,
            "total_revenue": round(r.total_revenue, 2),
            "is_ac": r.is_predominantly_ac,
            "avg_daily_passengers": r.avg_daily_passengers
        }
        for r in routes
    ]

@router.get("/stops")
def get_stop_analytics(
    db: Session = Depends(get_db),
    limit: int = Query(30)
):
    stops = db.query(Stop).order_by(Stop.monthly_boardings.desc()).limit(limit).all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "corridor": s.corridor,
            "monthly_boardings": s.monthly_boardings,
            "monthly_alightings": s.monthly_alightings,
            "is_major_hub": s.is_major_hub,
            "latitude": s.latitude,
            "longitude": s.longitude
        }
        for s in stops
    ]
