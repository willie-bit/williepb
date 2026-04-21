"""Monthly P&L calculation.

Two components, kept separate to avoid mixing cash flow with investment returns:

1. **Realized**: sum of (sell_price - avg_cost_at_time) × qty - fees, computed
   from `Transaction` rows of kind SELL/DIVIDEND/INTEREST - FEE for the month.
   MVP uses recorded `price` on SELL × qty minus `cost_basis_avg × qty` from
   the Asset at the time of the sale (approximation; exact lot tracking later).
2. **Unrealized change**: ΔNetWorthFromPositions between month-end snapshots,
   minus cashflow_in/out of that month (so external inflows don't inflate
   "returns").
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, CashFlowEvent, CashFlowKind, Transaction, TxSide
from app.services.snapshot import snapshot_on


@dataclass(slots=True)
class MonthlyPnLRow:
    year_month: str
    realized: Decimal
    unrealized_change: Decimal
    cashflow_in: Decimal
    cashflow_out: Decimal
    net: Decimal


def _first_last(year: int, month: int) -> tuple[date, date]:
    _, last = monthrange(year, month)
    return date(year, month, 1), date(year, month, last)


def _prev_month_end(year: int, month: int) -> date:
    first = date(year, month, 1)
    return first - timedelta(days=1)


def realized_for_month(db: Session, household_id: int, year: int, month: int) -> Decimal:
    start, end = _first_last(year, month)
    stmt = (
        select(Transaction, Asset)
        .join(Asset, Transaction.asset_id == Asset.id)
        .where(
            Asset.household_id == household_id,
            Transaction.trade_date >= start,
            Transaction.trade_date <= end,
        )
    )
    total = Decimal("0")
    for tx, asset in db.execute(stmt).all():
        qty = Decimal(str(tx.quantity or 0))
        price = Decimal(str(tx.price or 0))
        fees = Decimal(str(tx.fees or 0))
        avg = Decimal(str(asset.cost_basis_avg or 0))
        if tx.side == TxSide.SELL:
            total += (price - avg) * qty - fees
        elif tx.side in (TxSide.DIVIDEND, TxSide.INTEREST):
            total += price * qty - fees
        elif tx.side == TxSide.FEE:
            total -= fees
    return total


def cashflow_for_month(
    db: Session, household_id: int, year: int, month: int
) -> tuple[Decimal, Decimal]:
    start, end = _first_last(year, month)
    stmt = select(CashFlowEvent).where(
        CashFlowEvent.household_id == household_id,
        CashFlowEvent.event_date >= start,
        CashFlowEvent.event_date <= end,
    )
    inflow = Decimal("0")
    outflow = Decimal("0")
    for ev in db.scalars(stmt).all():
        amt = Decimal(str(ev.amount))
        if ev.kind == CashFlowKind.INCOME:
            inflow += amt
        else:
            outflow += amt
    return inflow, outflow


def monthly_pnl(
    db: Session, household_id: int, months: int = 6
) -> list[MonthlyPnLRow]:
    today = date.today()
    year, month = today.year, today.month
    out: list[MonthlyPnLRow] = []
    for _ in range(months):
        _, end = _first_last(year, month)
        prev_end = _prev_month_end(year, month)

        prev_snap = snapshot_on(db, household_id, prev_end)
        curr_snap = snapshot_on(db, household_id, end)

        start_nw = Decimal(str(prev_snap.net_worth)) if prev_snap else Decimal("0")
        end_nw = Decimal(str(curr_snap.net_worth)) if curr_snap else Decimal("0")

        realized = realized_for_month(db, household_id, year, month)
        inflow, outflow = cashflow_for_month(db, household_id, year, month)

        # unrealized change = Δnet worth - cashflow contributions - realized
        unrealized = end_nw - start_nw - (inflow - outflow) - realized
        net = realized + unrealized + inflow - outflow

        out.append(
            MonthlyPnLRow(
                year_month=f"{year:04d}-{month:02d}",
                realized=realized,
                unrealized_change=unrealized,
                cashflow_in=inflow,
                cashflow_out=outflow,
                net=net,
            )
        )
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(out))
