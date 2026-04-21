from datetime import date
from decimal import Decimal

from app.models import (
    Account,
    Asset,
    AssetType,
    Household,
    Member,
    PriceQuote,
    Role,
    ValuationSource,
)
from app.services.valuation import value_asset


def _seed_household(session) -> tuple[Household, Member, Account]:
    hh = Household(name="Lee 가족", base_currency="KRW")
    session.add(hh)
    session.flush()
    m = Member(household_id=hh.id, name="아빠", role=Role.OWNER)
    session.add(m)
    session.flush()
    acct = Account(
        household_id=hh.id,
        owner_member_id=m.id,
        institution_code="kiwoom",
        account_name="키움 위탁",
    )
    session.add(acct)
    session.flush()
    return hh, m, acct


def test_manual_value_assets_use_manual_figure(session):
    hh, m, _ = _seed_household(session)
    asset = Asset(
        household_id=hh.id,
        account_id=None,
        asset_type=AssetType.REAL_ESTATE,
        label="서울 아파트",
        manual_value=Decimal("1500000000"),
        valuation_source=ValuationSource.MANUAL,
    )
    session.add(asset)
    session.flush()

    result = value_asset(session, asset, on_date=date(2026, 4, 21))
    assert result.value == Decimal("1500000000")
    assert result.source == "manual"


def test_stock_uses_latest_quote_times_quantity(session):
    hh, m, acct = _seed_household(session)
    asset = Asset(
        household_id=hh.id,
        account_id=acct.id,
        asset_type=AssetType.STOCK,
        label="삼성전자",
        symbol="005930",
        quantity=Decimal("10"),
        cost_basis_avg=Decimal("70000"),
        valuation_source=ValuationSource.DAILY,
    )
    session.add(asset)
    session.add(
        PriceQuote(
            asset_key="STOCK:005930",
            quote_date=date(2026, 4, 20),
            price=Decimal("85000"),
            currency="KRW",
            source="krx",
        )
    )
    session.flush()

    result = value_asset(session, asset, on_date=date(2026, 4, 21))
    assert result.value == Decimal("850000")
    assert result.unit_price == Decimal("85000")
    assert result.source == "krx"


def test_missing_price_reported(session):
    hh, m, acct = _seed_household(session)
    asset = Asset(
        household_id=hh.id,
        account_id=acct.id,
        asset_type=AssetType.STOCK,
        label="미등록종목",
        symbol="999999",
        quantity=Decimal("1"),
    )
    session.add(asset)
    session.flush()

    result = value_asset(session, asset, on_date=date(2026, 4, 21))
    assert result.missing_price is True
    assert result.value == Decimal("0")


def test_usd_asset_converted_via_fx_quote(session):
    hh, m, acct = _seed_household(session)
    asset = Asset(
        household_id=hh.id,
        account_id=acct.id,
        asset_type=AssetType.STOCK,
        label="Apple",
        symbol="AAPL",
        quantity=Decimal("2"),
        currency="USD",
    )
    session.add(asset)
    session.add(
        PriceQuote(
            asset_key="STOCK:AAPL",
            quote_date=date(2026, 4, 20),
            price=Decimal("200"),
            currency="USD",
            source="manual",
        )
    )
    session.add(
        PriceQuote(
            asset_key="FX:USD/KRW",
            quote_date=date(2026, 4, 20),
            price=Decimal("1400"),
            currency="KRW",
            source="ecos_fx",
        )
    )
    session.flush()

    result = value_asset(session, asset, on_date=date(2026, 4, 21))
    # 2 × 200 × 1400
    assert result.value == Decimal("560000")
