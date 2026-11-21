from fastapi import APIRouter
from backend.app.schemas.schemas import SimulationRequest, SimulationResponse
from backend.app.services.simulation_service import simulation_service

router = APIRouter()

@router.post("/shift", response_model=SimulationResponse)
def simulate_demand_shift(req: SimulationRequest):
    return simulation_service.run_simulation(req)
