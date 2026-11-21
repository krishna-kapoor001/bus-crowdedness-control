from sqlalchemy import Column, Integer, String, Float, Boolean, Date, DateTime, Text, Index
from sqlalchemy.sql import func
from backend.app.database import Base

class Stop(Base):
    __tablename__ = "stops"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    corridor = Column(String(100), default="Delhi NCT")
    monthly_boardings = Column(Integer, default=0)
    monthly_alightings = Column(Integer, default=0)
    is_major_hub = Column(Boolean, default=False)

    __table_args__ = (
        Index("idx_stop_name", "name"),
        Index("idx_stop_coords", "latitude", "longitude"),
    )

class Route(Base):
    __tablename__ = "routes"

    route_id = Column(String(50), primary_key=True, index=True)
    direction = Column(String(20), default="UP") # UP / DOWN / CIRCULAR
    origin = Column(String(255))
    destination = Column(String(255))
    total_tickets = Column(Integer, default=0)
    total_passengers = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    is_predominantly_ac = Column(Boolean, default=False)
    avg_daily_passengers = Column(Float, default=0.0)

    __table_args__ = (
        Index("idx_route_direction", "direction"),
    )

class HourlyDemand(Base):
    __tablename__ = "hourly_demand"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    route_id = Column(String(50), index=True, nullable=False)
    date = Column(String(20), index=True)
    day_of_week = Column(Integer, index=True) # 0=Monday, 6=Sunday
    hour = Column(Integer, index=True) # 0-23
    is_weekend = Column(Integer, default=0) # 0 or 1
    passengers = Column(Integer, default=0)
    tickets = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    ac_trips = Column(Integer, default=0)

    __table_args__ = (
        Index("idx_demand_route_hour", "route_id", "day_of_week", "hour"),
        Index("idx_demand_date_hour", "date", "hour"),
    )

class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    model_name = Column(String(100), nullable=False)
    dataset_split = Column(String(100), default="Chronological (Oct 1-24 Train / Oct 25-30 Test)")
    train_samples = Column(Integer, default=0)
    test_samples = Column(Integer, default=0)
    mae = Column(Float, default=0.0)
    rmse = Column(Float, default=0.0)
    r2_score = Column(Float, default=0.0)
    baseline_mae = Column(Float, default=0.0)
    improvement_pct = Column(Float, default=0.0)
    feature_importance_json = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SimulationScenario(Base):
    __tablename__ = "simulation_scenarios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), default="Custom Scenario")
    demand_multiplier = Column(Float, default=1.0)
    peak_shift_factor = Column(Float, default=0.0)
    selected_route = Column(String(50), nullable=True)
    result_summary = Column(Text, default="{}")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
