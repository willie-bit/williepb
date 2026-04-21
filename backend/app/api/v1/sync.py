from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.deps import AuthContext, get_auth_context
from app.db.session import get_db
from app.models import Account
from app.services.snapshot import write_snapshot
from app.services.sync import sync_account, sync_prices

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncResult(BaseModel):
    prices_written: int
    accounts_synced: int
    errors: list[str]
    snapshot_written: bool


@router.post("/household", response_model=SyncResult)
def sync_household(
    on_date: date | None = None,
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> SyncResult:
    target = on_date or date.today()
    report = sync_prices(db, target, household_id=ctx.household_id)
    write_snapshot(db, ctx.household_id, target)
    db.commit()
    return SyncResult(
        prices_written=report.prices_written,
        accounts_synced=0,
        errors=report.errors,
        snapshot_written=True,
    )


@router.post("/account/{account_id}", response_model=SyncResult)
def sync_one_account(
    account_id: int,
    credentials: dict = Body(default_factory=dict),
    ctx: AuthContext = Depends(get_auth_context),
    db: Session = Depends(get_db),
) -> SyncResult:
    account = db.get(Account, account_id)
    if account is None or account.household_id != ctx.household_id:
        raise HTTPException(status_code=404, detail="Account not found")
    report = sync_account(db, account_id, credentials)
    db.commit()
    return SyncResult(
        prices_written=0,
        accounts_synced=report.accounts_synced,
        errors=report.errors,
        snapshot_written=False,
    )
