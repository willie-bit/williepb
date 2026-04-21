from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, Numeric, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class HouseholdDailySnapshot(Base):
    """End-of-day snapshot of a household's net worth.

    Stored daily by the snapshot job so we can compute month-over-month P&L,
    YTD returns, and drawdown later without re-reading every historical price.
    """

    __tablename__ = "household_daily_snapshots"
    __table_args__ = (
        UniqueConstraint("household_id", "snapshot_date", name="uq_snap_hh_date"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    household_id: Mapped[int] = mapped_column(
        ForeignKey("households.id", ondelete="CASCADE"), index=True, nullable=False
    )
    snapshot_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    total_assets: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    total_liabilities: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    net_worth: Mapped[float] = mapped_column(Numeric(20, 2), nullable=False)
    by_asset_type: Mapped[dict] = mapped_column(JSON, nullable=False)
    by_member: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    household: Mapped["Household"] = relationship(back_populates="snapshots")  # noqa: F821
