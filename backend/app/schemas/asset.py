from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.asset import AssetType, ValuationSource


class AssetCreate(BaseModel):
    household_id: int
    account_id: int | None = None
    asset_type: AssetType
    label: str
    symbol: str | None = None
    currency: str = "KRW"
    quantity: Decimal = Decimal("0")
    cost_basis_avg: Decimal | None = None
    manual_value: Decimal | None = None
    valuation_source: ValuationSource = ValuationSource.MANUAL
    asset_metadata: dict | None = None


class AssetUpdate(BaseModel):
    label: str | None = None
    quantity: Decimal | None = None
    cost_basis_avg: Decimal | None = None
    manual_value: Decimal | None = None
    valuation_source: ValuationSource | None = None
    asset_metadata: dict | None = None


class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    household_id: int
    account_id: int | None
    asset_type: AssetType
    label: str
    symbol: str | None
    currency: str
    quantity: Decimal
    cost_basis_avg: Decimal | None
    manual_value: Decimal | None
    valuation_source: ValuationSource
    asset_metadata: dict | None
    created_at: datetime
