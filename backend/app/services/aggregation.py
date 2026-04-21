"""Household-level aggregation.

Splits assets / liabilities across members based on `Account.ownership_shares`
(or falls back to 100% to `owner_member_id`). Liabilities always attribute to
`owner_member_id` for MVP (joint loans can be modelled later).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Account, Asset, AssetType, Household, Liability, Member
from app.services.valuation import ValuedAsset, value_asset


@dataclass(slots=True)
class MemberAggregate:
    member_id: int
    member_name: str
    assets: Decimal = Decimal("0")
    liabilities: Decimal = Decimal("0")

    @property
    def net_worth(self) -> Decimal:
        return self.assets - self.liabilities


@dataclass(slots=True)
class HouseholdAggregate:
    household_id: int
    as_of: date
    base_currency: str
    total_assets: Decimal = Decimal("0")
    total_liabilities: Decimal = Decimal("0")
    by_asset_type: dict[AssetType, Decimal] = field(default_factory=dict)
    by_member: dict[int, MemberAggregate] = field(default_factory=dict)
    valued_assets: list[ValuedAsset] = field(default_factory=list)

    @property
    def net_worth(self) -> Decimal:
        return self.total_assets - self.total_liabilities


def _split_asset(
    asset: Asset, account: Account | None, value: Decimal
) -> list[tuple[int, Decimal]]:
    """Return [(member_id, amount)]. If account has ownership_shares, honour them.

    Shares are validated loosely — ratios are normalized to sum to 1.0 so a
    typo (0.5 + 0.6) doesn't silently inflate totals.
    """
    if account and account.ownership_shares:
        items = [(int(k), Decimal(str(v))) for k, v in account.ownership_shares.items()]
        total_ratio = sum((r for _, r in items), Decimal("0"))
        if total_ratio > 0:
            return [(mid, value * ratio / total_ratio) for mid, ratio in items]
    if account:
        return [(account.owner_member_id, value)]
    return []  # unlinked asset (e.g. 실물) — caller handles household-level attribution


def aggregate_household(db: Session, household_id: int, on_date: date) -> HouseholdAggregate:
    household = db.get(Household, household_id)
    if household is None:
        raise ValueError(f"Household {household_id} not found")

    agg = HouseholdAggregate(
        household_id=household_id,
        as_of=on_date,
        base_currency=household.base_currency,
    )
    for m in household.members:
        agg.by_member[m.id] = MemberAggregate(member_id=m.id, member_name=m.name)

    assets = db.scalars(
        select(Asset).where(Asset.household_id == household_id)
    ).all()
    accounts = {a.id: a for a in db.scalars(
        select(Account).where(Account.household_id == household_id)
    ).all()}

    for asset in assets:
        valued = value_asset(db, asset, on_date, base_ccy=household.base_currency)
        agg.valued_assets.append(valued)
        if valued.value == 0:
            continue
        agg.total_assets += valued.value
        agg.by_asset_type[asset.asset_type] = (
            agg.by_asset_type.get(asset.asset_type, Decimal("0")) + valued.value
        )
        account = accounts.get(asset.account_id) if asset.account_id else None
        splits = _split_asset(asset, account, valued.value)
        if not splits:
            continue
        for mid, amount in splits:
            if mid in agg.by_member:
                agg.by_member[mid].assets += amount

    liabilities = db.scalars(
        select(Liability).where(Liability.household_id == household_id)
    ).all()
    for liab in liabilities:
        bal = Decimal(str(liab.balance))
        agg.total_liabilities += bal
        if liab.owner_member_id in agg.by_member:
            agg.by_member[liab.owner_member_id].liabilities += bal

    return agg


def list_members(db: Session, household_id: int) -> list[Member]:
    return list(
        db.scalars(select(Member).where(Member.household_id == household_id)).all()
    )
