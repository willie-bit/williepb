from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from app.models.liability import LiabilityType, RateType


class LiabilityCreate(BaseModel):
    household_id: int
    owner_member_id: int
    institution_code: str | None = None
    liability_type: LiabilityType
    label: str
    principal: Decimal
    balance: Decimal
    interest_rate: Decimal | None = None
    rate_type: RateType = RateType.FIXED
    currency: str = "KRW"
    start_date: date | None = None
    maturity_date: date | None = None


class LiabilityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    household_id: int
    owner_member_id: int
    institution_code: str | None
    liability_type: LiabilityType
    label: str
    principal: Decimal
    balance: Decimal
    interest_rate: Decimal | None
    rate_type: RateType
    currency: str
    start_date: date | None
    maturity_date: date | None
    created_at: datetime
