from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

# --- Overview Schemas ---
class OverviewKPIs(BaseModel):
    estimated_passenger_demand: int
    analyzed_transport_routes: int
    high_demand_corridors: int
    predicted_peak_crowding: str
    model_prediction_confidence: float
    data_freshness: str
    dataset_records: int

class DemandTrendPoint(BaseModel):
    hour: int
    time_label: str
    passengers: int
    is_peak: bool

class PeakComparison(BaseModel):
    morning_peak_avg: int
    evening_peak_avg: int
    midday_offpeak_avg: int
    night_offpeak_avg: int
    peak_share_pct: float
    morning_share_pct: Optional[float] = 33.4
    evening_share_pct: Optional[float] = 28.8

class RouteRanking(BaseModel):
    rank: int
    route_id: str
    origin: str
    destination: str
    daily_passengers: float
    crowd_category: str # LOW, MODERATE, HIGH, VERY HIGH
    confidence: float
    is_ac: bool

class HeatmapCell(BaseModel):
    corridor: str
    hour: int
    demand_level: str # LOW, MODERATE, HIGH, VERY HIGH
    volume: int

class OverviewResponse(BaseModel):
    kpis: OverviewKPIs
    demand_trends: List[DemandTrendPoint]
    peak_comparison: PeakComparison
    top_crowded_routes: List[RouteRanking]
    heatmap: List[HeatmapCell]
    data_notes: str

# --- Journey Planner Schemas ---
class JourneySearchRequest(BaseModel):
    origin: str
    destination: str
    departure_date: Optional[str] = "2026-10-28"
    departure_time: Optional[str] = "08:30"
    prefer_less_crowded: Optional[bool] = False

class JourneyStep(BaseModel):
    route_id: str
    from_stop: str
    to_stop: str
    duration_mins: int
    crowd_level: str # LOW, MODERATE, HIGH, VERY HIGH
    crowd_score: int # 0 - 100
    comfort_label: Optional[str] = "Standing Room"
    stretch_name: Optional[str] = None
    onboard_pax_est: Optional[int] = None
    is_ac: bool
    confidence: float

class JourneyAlternative(BaseModel):
    id: str
    badge: str # 'FASTEST', 'LEAST CROWDED', 'FEWEST TRANSFERS', 'RECOMMENDED', 'SEATS AVAILABLE'
    total_duration_mins: int
    crowd_level: str
    crowd_score: int
    comfort_label: Optional[str] = "Standing Room"
    stretch_summary: Optional[str] = None
    departure_time_label: Optional[str] = None
    departure_shift_mins: Optional[int] = 0
    transfers: int
    bus_routes: List[str]
    stops_count: int
    stops_list: List[str]
    estimated_waiting_time_mins: int
    prediction_confidence: float
    recommendation_explanation: str
    steps: List[JourneyStep]
    route_coordinates: Optional[List[List[float]]] = None
    service_type: Optional[str] = "REGULAR" # 'DIRECT_EXPRESS' or 'REGULAR'
    service_badge: Optional[str] = "Regular (All Stops)"
    time_saved_mins: Optional[int] = 0
    intermediate_stops: Optional[List[str]] = None
    skipped_stops: Optional[List[str]] = None

class JourneySearchResponse(BaseModel):
    origin: str
    destination: str
    departure_time: str
    prefer_less_crowded: bool
    alternatives: List[JourneyAlternative]

# --- Analytics Schemas ---
class HourlyDistributionItem(BaseModel):
    hour: int
    time_label: str
    weekday_passengers: int
    weekend_passengers: int

class AnalyticsFilterRequest(BaseModel):
    route: Optional[str] = None
    corridor: Optional[str] = None
    time_window: Optional[str] = "ALL" # ALL, MORNING_PEAK, EVENING_PEAK, OFF_PEAK

# --- CrowdShift Simulator Schemas ---
class SimulationRequest(BaseModel):
    demand_multiplier: float = Field(1.15, ge=0.5, le=2.0)
    peak_shift_factor: float = Field(-0.15, ge=-0.5, le=0.5)
    selected_route: Optional[str] = "ALL"

class CorridorImpact(BaseModel):
    corridor_name: str
    original_demand: int
    simulated_demand: int
    delta_pct: float
    original_crowd_level: str
    simulated_crowd_level: str
    impact_level: str # SEVERE, MODERATE, MINIMAL, RELIEVED

class AlternativeWindow(BaseModel):
    time_slot: str
    crowd_reduction_pct: float
    recommended_for: str

class SimulationResponse(BaseModel):
    scenario_name: str
    demand_multiplier: float
    peak_shift_factor: float
    total_original_demand: int
    total_simulated_demand: int
    system_wide_delta_pct: float
    corridors: List[CorridorImpact]
    shift_recommendations: List[AlternativeWindow]
    mathematical_rationale: str

# --- Model Information Schemas ---
class ModelMetricsResponse(BaseModel):
    model_name: str
    dataset_split: str
    train_samples: int
    test_samples: int
    mae: float
    rmse: float
    r2_score: float
    baseline_mae: float
    improvement_pct: float
    residual_std: float
    features: List[str]
    confidence_methodology: str
