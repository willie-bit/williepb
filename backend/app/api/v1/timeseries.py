from datetime import date, timedelta
from decimal import Decimal

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.models import HouseholdDailySnapshot
from app.services.dashboard import build_dashboard
from app.services.snapshot import write_snapshot

router = APIRouter(prefix="/timeseries", tags=["timeseries"])


class NetWorthPoint(BaseModel):
    date: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal


class NetWorthSeries(BaseModel):
    points: list[NetWorthPoint]


@router.get("/net-worth", response_model=NetWorthSeries)
def net_worth_series(
    days: int = 90,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> NetWorthSeries:
    """Return the last `days` days of snapshotted net worth.

    If no snapshot exists for today yet, compute one on the fly so the chart
    always ends at a current value (the seed/test data never populates history).
    """
    since = date.today() - timedelta(days=days)
    rows = list(
        db.scalars(
            select(HouseholdDailySnapshot)
            .where(
                HouseholdDailySnapshot.household_id == ctx.household_id,
                HouseholdDailySnapshot.snapshot_date >= since,
            )
            .order_by(HouseholdDailySnapshot.snapshot_date)
        ).all()
    )

    if not rows or rows[-1].snapshot_date != date.today():
        today_snap = write_snapshot(db, ctx.household_id, date.today())
        db.commit()
        if not rows or rows[-1].snapshot_date != today_snap.snapshot_date:
            rows.append(today_snap)

    points = [
        NetWorthPoint(
            date=r.snapshot_date,
            total_assets=Decimal(str(r.total_assets)),
            total_liabilities=Decimal(str(r.total_liabilities)),
            net_worth=Decimal(str(r.net_worth)),
        )
        for r in rows
    ]
    return NetWorthSeries(points=points)
