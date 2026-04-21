from datetime import date

from fastapi import APIRouter, Body, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Household
from app.services.snapshot import write_snapshot
from app.services.sync import sync_account, sync_prices

router = APIRouter(prefix="/sync", tags=["sync"])


class SyncResult(BaseModel):
    prices_written: int
    accounts_synced: int
    errors: list[str]
    snapshot_written: bool


@router.post("/household/{household_id}", response_model=SyncResult)
def sync_household(
    household_id: int,
    on_date: date | None = None,
    db: Session = Depends(get_db),
) -> SyncResult:
    """Fetch market prices for this household's symbols, then write a snapshot.

    Account-level credential sync is triggered separately via `/sync/account/{id}`
    because credentials are caller-supplied and may vary per request.
    """
    if db.get(Household, household_id) is None:
        raise HTTPException(status_code=404, detail="Household not found")
    target = on_date or date.today()
    report = sync_prices(db, target, household_id=household_id)
    write_snapshot(db, household_id, target)
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
    db: Session = Depends(get_db),
) -> SyncResult:
    """Trigger account-level holding sync.

    `credentials` shape depends on the institution adapter. Examples:
      - CSV-based: {"csv_path": "/data/imports/kiwoom/2026-04-20.csv"}
      - Upbit:    {"access_key": "...", "secret_key": "..."}
    """
    report = sync_account(db, account_id, credentials)
    db.commit()
    return SyncResult(
        prices_written=0,
        accounts_synced=report.accounts_synced,
        errors=report.errors,
        snapshot_written=False,
    )
