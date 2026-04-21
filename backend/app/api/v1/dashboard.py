from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Household
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/{household_id}", response_model=DashboardResponse)
def get_dashboard(
    household_id: int,
    on_date: date | None = None,
    db: Session = Depends(get_db),
) -> DashboardResponse:
    if db.get(Household, household_id) is None:
        raise HTTPException(status_code=404, detail="Household not found")
    return build_dashboard(db, household_id, on_date or date.today())
