from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Account(Base):
    """A container at a specific institution (bank account, brokerage account, wallet).

    `institution_code` identifies the integration adapter (e.g. "kb_kookmin",
    "woori", "kiwoom", "nh_invest", "upbit"). A stable code lets us swap
    implementations without touching data.
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_member_id: Mapped[int] = mapped_column(
        ForeignKey("members.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    institution_code: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    account_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_number_masked: Mapped[str | None] = mapped_column(String(64))
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    ownership_shares: Mapped[dict | None] = mapped_column(JSON)
    """Optional {member_id: ratio} for joint ownership. If null, owner_member_id holds 100%."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    household: Mapped["Household"] = relationship(back_populates="accounts")  # noqa: F821
    assets: Mapped[list["Asset"]] = relationship(  # noqa: F821
        back_populates="account", cascade="all, delete-orphan"
    )
