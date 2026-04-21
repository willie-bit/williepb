from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class PriceQuote(Base):
    """Daily closing price per (symbol, currency, source).

    Kept flat to swap in TimescaleDB later without schema changes.
    """

    __tablename__ = "price_quotes"
    __table_args__ = (
        UniqueConstraint("asset_key", "quote_date", "source", name="uq_priceq_key_date_src"),
        Index("ix_priceq_key_date", "asset_key", "quote_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    asset_key: Mapped[str] = mapped_column(String(80), nullable=False)
    """Composite identifier like "STOCK:005930", "CRYPTO:KRW-BTC", "FX:USD/KRW"."""
    quote_date: Mapped[date] = mapped_column(Date, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(20, 6), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)
    source: Mapped[str] = mapped_column(String(40), nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
