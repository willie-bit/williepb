from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HouseholdCreate(BaseModel):
    name: str
    base_currency: str = "KRW"


class HouseholdOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    base_currency: str
    created_at: datetime
