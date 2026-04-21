from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class AllocationSlice(BaseModel):
    key: str
    label: str
    value: Decimal
    ratio: float


class MemberBreakdown(BaseModel):
    member_id: int
    member_name: str
    assets: Decimal
    liabilities: Decimal
    net_worth: Decimal


class MonthlyPnL(BaseModel):
    year_month: str  # "YYYY-MM"
    realized: Decimal
    unrealized_change: Decimal
    cashflow_in: Decimal
    cashflow_out: Decimal
    net: Decimal


class DashboardResponse(BaseModel):
    household_id: int
    as_of: date
    total_assets: Decimal
    total_liabilities: Decimal
    net_worth: Decimal
    by_asset_type: list[AllocationSlice]
    by_member: list[MemberBreakdown]
    recent_monthly_pnl: list[MonthlyPnL]
