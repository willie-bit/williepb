from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Household(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    members: Mapped[list["Member"]] = relationship(  # noqa: F821
        back_populates="household", cascade="all, delete-orphan"
    )
    accounts: Mapped[list["Account"]] = relationship(  # noqa: F821
        back_populates="household", cascade="all, delete-orphan"
    )
    liabilities: Mapped[list["Liability"]] = relationship(  # noqa: F821
        back_populates="household", cascade="all, delete-orphan"
    )
    snapshots: Mapped[list["HouseholdDailySnapshot"]] = relationship(  # noqa: F821
        back_populates="household", cascade="all, delete-orphan"
    )
