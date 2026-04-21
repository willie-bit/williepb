import enum
from datetime import date, datetime

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class TxSide(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"
    DIVIDEND = "DIVIDEND"
    INTEREST = "INTEREST"
    FEE = "FEE"
    TRANSFER_IN = "TRANSFER_IN"
    TRANSFER_OUT = "TRANSFER_OUT"


class Transaction(Base):
    """Realized-event log tied to an asset (e.g. a stock trade, crypto buy)."""

    __tablename__ = "asset_transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="CASCADE"), index=True, nullable=False
    )
    trade_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    side: Mapped[TxSide] = mapped_column(Enum(TxSide), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(28, 8), nullable=False)
    price: Mapped[float | None] = mapped_column(Numeric(20, 6))
    fees: Mapped[float] = mapped_column(Numeric(20, 4), default=0, nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    memo: Mapped[str | None] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )


class CashFlowKind(str, enum.Enum):
    INCOME = "INCOME"
    EXPENSE = "EXPENSE"
    CARD_CHARGE = "CARD_CHARGE"
    LOAN_PAYMENT = "LOAN_PAYMENT"


class CashFlowEvent(Base):
    """Household-level cash in/out (salary, card bill, utility, loan installment)."""

    __tablename__ = "cashflow_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True, nullable=False
    )
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id", ondelete="SET NULL"))
    event_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    kind: Mapped[CashFlowKind] = mapped_column(Enum(CashFlowKind), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(64))
    amount: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    counterparty: Mapped[str | None] = mapped_column(String(160))
    memo: Mapped[str | None] = mapped_column(String(240))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
