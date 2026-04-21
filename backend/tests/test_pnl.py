from datetime import date
from decimal import Decimal

from app.models import (
    Asset,
    AssetType,
    CashFlowEvent,
    CashFlowKind,
    Household,
    HouseholdDailySnapshot,
    Member,
    Role,
    Transaction,
    TxSide,
)
from app.services.pnl import monthly_pnl


def test_monthly_pnl_combines_realized_and_unrealized(session):
    hh = Household(name="가족", base_currency="KRW")
    session.add(hh)
    session.flush()
    m = Member(household_id=hh.id, name="아빠", role=Role.OWNER)
    session.add(m)
    session.flush()

    # Snapshots for two consecutive month-ends (use current year/month for determinism
    # we just stuff in the last 2 months).
    today = date.today()
    if today.month == 1:
        prev_year, prev_month = today.year - 1, 12
    else:
        prev_year, prev_month = today.year, today.month - 1

    from calendar import monthrange

    prev_end = date(prev_year, prev_month, monthrange(prev_year, prev_month)[1])
    curr_end = date(today.year, today.month, monthrange(today.year, today.month)[1])

    session.add(
        HouseholdDailySnapshot(
            household_id=hh.id,
            snapshot_date=prev_end,
            total_assets=Decimal("10000000"),
            total_liabilities=Decimal("0"),
            net_worth=Decimal("10000000"),
            by_asset_type={},
            by_member={},
        )
    )
    session.add(
        HouseholdDailySnapshot(
            household_id=hh.id,
            snapshot_date=curr_end,
            total_assets=Decimal("11500000"),
            total_liabilities=Decimal("0"),
            net_worth=Decimal("11500000"),
            by_asset_type={},
            by_member={},
        )
    )

    # Realized: a SELL with price 120,000 of an asset with avg 100,000, qty 1
    asset = Asset(
        household_id=hh.id,
        asset_type=AssetType.STOCK,
        label="어떤종목",
        symbol="000000",
        quantity=Decimal("0"),
        cost_basis_avg=Decimal("100000"),
    )
    session.add(asset)
    session.flush()
    session.add(
        Transaction(
            asset_id=asset.id,
            trade_date=date(today.year, today.month, 5),
            side=TxSide.SELL,
            quantity=Decimal("1"),
            price=Decimal("120000"),
            fees=Decimal("0"),
        )
    )
    # Cashflow: 급여 +500,000, 카드 -300,000
    session.add(
        CashFlowEvent(
            household_id=hh.id,
            event_date=date(today.year, today.month, 25),
            kind=CashFlowKind.INCOME,
            amount=Decimal("500000"),
        )
    )
    session.add(
        CashFlowEvent(
            household_id=hh.id,
            event_date=date(today.year, today.month, 10),
            kind=CashFlowKind.CARD_CHARGE,
            amount=Decimal("300000"),
        )
    )
    session.flush()

    rows = monthly_pnl(session, hh.id, months=2)
    assert len(rows) == 2
    current = rows[-1]
    assert current.year_month == f"{today.year:04d}-{today.month:02d}"
    assert current.realized == Decimal("20000")  # (120k - 100k) × 1
    assert current.cashflow_in == Decimal("500000")
    assert current.cashflow_out == Decimal("300000")
    # Δnw = 1,500,000 ; cashflow net = +200,000 ; realized = 20,000
    # unrealized = 1,500,000 - 200,000 - 20,000 = 1,280,000
    assert current.unrealized_change == Decimal("1280000")
    # net = realized + unrealized + inflow - outflow
    assert current.net == Decimal("20000") + Decimal("1280000") + Decimal("200000")
