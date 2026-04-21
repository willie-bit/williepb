from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.models.member import Role


class MemberCreate(BaseModel):
    household_id: int
    name: str
    email: EmailStr | None = None
    role: Role = Role.VIEWER


class MemberOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    household_id: int
    name: str
    email: str | None
    role: Role
    created_at: datetime
