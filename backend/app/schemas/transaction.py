from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.transaction import TxSide


class TransactionCreate(BaseModel):
    asset_id: int
    trade_date: date
    side: TxSide
    quantity: Decimal
    price: Decimal | None = None
    fees: Decimal = Decimal("0")
    currency: str = "KRW"
    memo: str | None = None


class TransactionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    asset_id: int
    trade_date: date
    side: TxSide
    quantity: Decimal
    price: Decimal | None
    fees: Decimal
    currency: str
    memo: str | None
    created_at: datetime
