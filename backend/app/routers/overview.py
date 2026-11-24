from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.services.demand_service import demand_service
from backend.app.schemas.schemas import OverviewResponse

router = APIRouter()

@router.get("", response_model=OverviewResponse)
def get_overview(db: Session = Depends(get_db)):
    return demand_service.get_overview(db)
