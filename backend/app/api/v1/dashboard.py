from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import build_dashboard

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def get_dashboard(
    on_date: date | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> DashboardResponse:
    return build_dashboard(db, ctx.household_id, on_date or date.today())
