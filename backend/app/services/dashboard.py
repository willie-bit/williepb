"""Dashboard assembly — combines aggregation + P&L into the API response."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import AssetType
from app.schemas.dashboard import (
    AllocationSlice,
    DashboardResponse,
    MemberBreakdown,
    MonthlyPnL,
)
from app.services.aggregation import aggregate_household
from app.services.pnl import monthly_pnl

ASSET_TYPE_LABELS: dict[AssetType, str] = {
    AssetType.REAL_ESTATE: "부동산",
    AssetType.STOCK: "주식",
    AssetType.ETF: "ETF",
    AssetType.FUND: "펀드",
    AssetType.PENSION: "연금",
    AssetType.CASH: "현금",
    AssetType.CRYPTO: "암호화폐",
    AssetType.GOLD_PHYSICAL: "금(현물)",
    AssetType.GOLD_FINANCIAL: "금(금융)",
    AssetType.VEHICLE: "자동차",
    AssetType.OTHER: "기타",
}


def build_dashboard(db: Session, household_id: int, on_date: date) -> DashboardResponse:
    agg = aggregate_household(db, household_id, on_date)

    slices: list[AllocationSlice] = []
    total = agg.total_assets if agg.total_assets > 0 else Decimal("1")
    for at, val in sorted(agg.by_asset_type.items(), key=lambda kv: kv[1], reverse=True):
        slices.append(
            AllocationSlice(
                key=at.value,
                label=ASSET_TYPE_LABELS.get(at, at.value),
                value=val,
                ratio=float(val / total),
            )
        )

    members = [
        MemberBreakdown(
            member_id=m.member_id,
            member_name=m.member_name,
            assets=m.assets,
            liabilities=m.liabilities,
            net_worth=m.net_worth,
        )
        for m in agg.by_member.values()
    ]

    pnl_rows = [
        MonthlyPnL(
            year_month=r.year_month,
            realized=r.realized,
            unrealized_change=r.unrealized_change,
            cashflow_in=r.cashflow_in,
            cashflow_out=r.cashflow_out,
            net=r.net,
        )
        for r in monthly_pnl(db, household_id, months=6)
    ]

    return DashboardResponse(
        household_id=household_id,
        as_of=on_date,
        total_assets=agg.total_assets,
        total_liabilities=agg.total_liabilities,
        net_worth=agg.net_worth,
        by_asset_type=slices,
        by_member=members,
        recent_monthly_pnl=pnl_rows,
    )
