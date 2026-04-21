import enum
from datetime import datetime

from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class AssetType(str, enum.Enum):
    REAL_ESTATE = "REAL_ESTATE"
    STOCK = "STOCK"
    ETF = "ETF"
    FUND = "FUND"
    PENSION = "PENSION"
    CASH = "CASH"
    CRYPTO = "CRYPTO"
    GOLD_PHYSICAL = "GOLD_PHYSICAL"
    GOLD_FINANCIAL = "GOLD_FINANCIAL"
    VEHICLE = "VEHICLE"
    OTHER = "OTHER"


class ValuationSource(str, enum.Enum):
    """How the current price is obtained."""

    REALTIME = "REALTIME"
    DAILY = "DAILY"
    MANUAL = "MANUAL"


class Asset(Base):
    """A valued position or holding.

    - For securities/crypto: `symbol` identifies the instrument (e.g. "005930",
      "KRW-BTC"), `quantity` × latest `PriceQuote` drives valuation.
    - For real estate / vehicle / other: `symbol` may be null; `metadata` carries
      address/VIN/etc and `manual_value` can override when no price feed is wired.
    """

    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id", ondelete="CASCADE"), index=True
    )
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_type: Mapped[AssetType] = mapped_column(Enum(AssetType), nullable=False, index=True)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    symbol: Mapped[str | None] = mapped_column(String(64), index=True)
    currency: Mapped[str] = mapped_column(String(8), default="KRW", nullable=False)

    quantity: Mapped[float] = mapped_column(Numeric(28, 8), default=0, nullable=False)
    cost_basis_avg: Mapped[float | None] = mapped_column(Numeric(20, 4))
    manual_value: Mapped[float | None] = mapped_column(Numeric(20, 2))
    """Override for assets without a price feed (real estate, vehicle, collectibles)."""

    valuation_source: Mapped[ValuationSource] = mapped_column(
        Enum(ValuationSource), default=ValuationSource.MANUAL, nullable=False
    )
    asset_metadata: Mapped[dict | None] = mapped_column("metadata", JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    account: Mapped["Account | None"] = relationship(back_populates="assets")  # noqa: F821
