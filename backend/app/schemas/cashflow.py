from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.transaction import CashFlowKind


class CashFlowEventCreate(BaseModel):
    household_id: int
    member_id: int | None = None
    event_date: date
    kind: CashFlowKind
    category: str | None = None
    amount: Decimal
    currency: str = "KRW"
    counterparty: str | None = None
    memo: str | None = None


class CashFlowEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    household_id: int
    member_id: int | None
    event_date: date
    kind: CashFlowKind
    category: str | None
    amount: Decimal
    currency: str
    counterparty: str | None
    memo: str | None
    created_at: datetime
