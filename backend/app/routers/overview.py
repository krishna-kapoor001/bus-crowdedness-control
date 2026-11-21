from fastapi import APIRouter
from backend.app.services.demand_service import demand_service
from backend.app.schemas.schemas import OverviewResponse

router = APIRouter()

@router.get("", response_model=OverviewResponse)
def get_overview():
    return demand_service.get_overview()
