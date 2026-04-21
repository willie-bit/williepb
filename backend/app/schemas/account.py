from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    household_id: int
    owner_member_id: int
    institution_code: str
    account_name: str
    account_number_masked: str | None = None
    currency: str = "KRW"
    ownership_shares: dict[str, float] | None = None


class AccountOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    household_id: int
    owner_member_id: int
    institution_code: str
    account_name: str
    account_number_masked: str | None
    currency: str
    ownership_shares: dict | None
    created_at: datetime
