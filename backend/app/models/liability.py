import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class LiabilityType(str, enum.Enum):
    MORTGAGE = "MORTGAGE"
    CREDIT_LOAN = "CREDIT_LOAN"
    CARD_INSTALLMENT = "CARD_INSTALLMENT"
    CARD_BALANCE = "CARD_BALANCE"
    PRIVATE_LOAN = "PRIVATE_LOAN"
    OTHER = "OTHER"


class RateType(str, enum.Enum):
    FIXED = "FIXED"
    FLOAT = "FLOAT"


class Liability(Base):
    __tablename__ = "liabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    institution_code: Mapped[str | None] = mapped_column(String(64), index=True)
    liability_type: Mapped[LiabilityType] = mapped_column(Enum(LiabilityType), nullable=False)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    principal: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    balance: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    interest_rate: Mapped[float | None] = mapped_column(Numeric(6, 4))
    rate_type: Mapped[RateType] = mapped_column(Enum(RateType), default=RateType.FIXED)
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    maturity_date: Mapped[date | None] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    household: Mapped["Household"] = relationship(back_populates="liabilities")  # noqa: F821
