"""Daily sync job — meant to be invoked by cron/Airflow/Celery Beat.

Steps:
1. Resolve target date (today by default).
2. For each household: call `sync_prices` + `write_snapshot`.
3. Account-level credential-bound syncs are NOT run here — they require
   user-provided secrets and belong in an authenticated on-demand path
   (or a user-scoped worker with encrypted creds, post-MVP).
"""

from __future__ import annotations

import logging
from datetime import date

from sqlalchemy import select

from app.db.session import SessionLocal, init_db
from app.models import Household
from app.services.snapshot import write_snapshot
from app.services.sync import SyncReport, sync_prices

logger = logging.getLogger(__name__)


def run_daily_sync(on_date: date | None = None) -> dict[int, SyncReport]:
    init_db()
    target = on_date or date.today()
    results: dict[int, SyncReport] = {}
    with SessionLocal() as db:
        households = list(db.scalars(select(Household)).all())
        for hh in households:
            logger.info("syncing household %s on %s", hh.id, target)
            report = sync_prices(db, target, household_id=hh.id)
            write_snapshot(db, hh.id, target)
            results[hh.id] = report
        db.commit()
    return results
