from datetime import date
from decimal import Decimal

from app.models import (
    Account,
    Asset,
    AssetType,
    Household,
    Liability,
    LiabilityType,
    Member,
    PriceQuote,
    Role,
    ValuationSource,
)
from app.services.aggregation import aggregate_household


def test_household_splits_by_ownership_shares(session):
    hh = Household(name="가족", base_currency="KRW")
    session.add(hh)
    session.flush()

    dad = Member(household_id=hh.id, name="아빠", role=Role.OWNER)
    mom = Member(household_id=hh.id, name="엄마", role=Role.CO_ADMIN)
    session.add_all([dad, mom])
    session.flush()

    # 50/50 joint brokerage
    joint = Account(
        household_id=hh.id,
        owner_member_id=dad.id,
        institution_code="nh_invest",
        account_name="공동명의",
        ownership_shares={str(dad.id): 0.5, str(mom.id): 0.5},
    )
    session.add(joint)
    session.flush()

    asset = Asset(
        household_id=hh.id,
        account_id=joint.id,
        asset_type=AssetType.STOCK,
        label="KODEX 200",
        symbol="069500",
        quantity=Decimal("100"),
        valuation_source=ValuationSource.DAILY,
    )
    session.add(asset)
    session.add(
        PriceQuote(
            asset_key="STOCK:069500",
            quote_date=date(2026, 4, 20),
            price=Decimal("10000"),
            currency="KRW",
            source="krx",
        )
    )

    # dad-only mortgage
    session.add(
        Liability(
            household_id=hh.id,
            owner_member_id=dad.id,
            liability_type=LiabilityType.MORTGAGE,
            label="주담대",
            principal=Decimal("500000000"),
            balance=Decimal("300000000"),
        )
    )
    session.flush()

    agg = aggregate_household(session, hh.id, on_date=date(2026, 4, 21))

    assert agg.total_assets == Decimal("1000000")  # 100 × 10,000
    assert agg.by_member[dad.id].assets == Decimal("500000")
    assert agg.by_member[mom.id].assets == Decimal("500000")
    assert agg.total_liabilities == Decimal("300000000")
    assert agg.by_member[dad.id].liabilities == Decimal("300000000")
    assert agg.by_member[mom.id].liabilities == Decimal("0")
    # net worth per member
    assert agg.by_member[dad.id].net_worth == Decimal("500000") - Decimal("300000000")
    assert agg.by_member[mom.id].net_worth == Decimal("500000")


def test_missing_shares_fall_back_to_owner(session):
    hh = Household(name="가족", base_currency="KRW")
    session.add(hh)
    session.flush()
    dad = Member(household_id=hh.id, name="아빠", role=Role.OWNER)
    session.add(dad)
    session.flush()
    acct = Account(
        household_id=hh.id,
        owner_member_id=dad.id,
        institution_code="upbit",
        account_name="업비트",
    )
    session.add(acct)
    session.flush()
    asset = Asset(
        household_id=hh.id,
        account_id=acct.id,
        asset_type=AssetType.CRYPTO,
        label="BTC",
        symbol="KRW-BTC",
        quantity=Decimal("0.1"),
    )
    session.add(asset)
    session.add(
        PriceQuote(
            asset_key="CRYPTO:KRW-BTC",
            quote_date=date(2026, 4, 20),
            price=Decimal("100000000"),
            currency="KRW",
            source="upbit",
        )
    )
    session.flush()

    agg = aggregate_household(session, hh.id, on_date=date(2026, 4, 21))
    assert agg.by_member[dad.id].assets == Decimal("10000000")
