"""Daily snapshot writer + reader.

Idempotent on (household_id, snapshot_date): rerunning the job for the same day
updates the existing row rather than duplicating it. This matters because the
daily batch may be retried after a partial failure.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import HouseholdDailySnapshot
from app.services.aggregation import HouseholdAggregate, aggregate_household


def write_snapshot(db: Session, household_id: int, on_date: date) -> HouseholdDailySnapshot:
    agg = aggregate_household(db, household_id, on_date)
    snap = db.scalar(
        select(HouseholdDailySnapshot).where(
            HouseholdDailySnapshot.household_id == household_id,
            HouseholdDailySnapshot.snapshot_date == on_date,
        )
    )
    payload = _serialize(agg)
    if snap is None:
        snap = HouseholdDailySnapshot(
            household_id=household_id,
            snapshot_date=on_date,
            **payload,
        )
        db.add(snap)
    else:
        for k, v in payload.items():
            setattr(snap, k, v)
    db.flush()
    return snap


def _serialize(agg: HouseholdAggregate) -> dict:
    return {
        "total_assets": agg.total_assets,
        "total_liabilities": agg.total_liabilities,
        "net_worth": agg.net_worth,
        "by_asset_type": {k.value: str(v) for k, v in agg.by_asset_type.items()},
        "by_member": {
            str(mid): {
                "name": m.member_name,
                "assets": str(m.assets),
                "liabilities": str(m.liabilities),
                "net_worth": str(m.net_worth),
            }
            for mid, m in agg.by_member.items()
        },
    }


def recent_snapshots(
    db: Session, household_id: int, days: int = 30
) -> list[HouseholdDailySnapshot]:
    since = date.today() - timedelta(days=days)
    return list(
        db.scalars(
            select(HouseholdDailySnapshot)
            .where(
                HouseholdDailySnapshot.household_id == household_id,
                HouseholdDailySnapshot.snapshot_date >= since,
            )
            .order_by(HouseholdDailySnapshot.snapshot_date)
        ).all()
    )


def snapshot_on(
    db: Session, household_id: int, target: date
) -> HouseholdDailySnapshot | None:
    return db.scalar(
        select(HouseholdDailySnapshot)
        .where(
            HouseholdDailySnapshot.household_id == household_id,
            HouseholdDailySnapshot.snapshot_date <= target,
        )
        .order_by(HouseholdDailySnapshot.snapshot_date.desc())
        .limit(1)
    )


def month_end_snapshots(
    db: Session, household_id: int, months: int = 6
) -> dict[str, HouseholdDailySnapshot | None]:
    """Return {'YYYY-MM': snapshot or None} for the last `months` months."""
    out: dict[str, HouseholdDailySnapshot | None] = {}
    today = date.today()
    # iterate month by month
    year, month = today.year, today.month
    for _ in range(months):
        # last day of month
        next_first = date(year + (1 if month == 12 else 0), (month % 12) + 1, 1)
        last_day = next_first - timedelta(days=1)
        ym = f"{year:04d}-{month:02d}"
        out[ym] = snapshot_on(db, household_id, last_day)
        # step back one month
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return dict(reversed(out.items()))
