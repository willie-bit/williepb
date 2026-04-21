"""Seed script — create one demo household with a handful of positions.

Run: `python -m scripts.seed` from `backend/` (after `williepb init-db`).
Safe to rerun — uses upserts keyed on (household.name, asset.label).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import select

from app.core.security import hash_password
from app.db.session import SessionLocal, init_db
from app.models import (
    Account,
    Asset,
    AssetType,
    CashFlowEvent,
    CashFlowKind,
    Household,
    Liability,
    LiabilityType,
    Member,
    PriceQuote,
    RateType,
    Role,
    User,
    ValuationSource,
)


def main() -> None:
    init_db()
    with SessionLocal() as db:
        hh = db.scalar(select(Household).where(Household.name == "샘플 가족"))
        if hh is None:
            hh = Household(name="샘플 가족", base_currency="KRW")
            db.add(hh)
            db.flush()

        dad = _upsert_member(db, hh.id, "아빠", Role.OWNER)
        mom = _upsert_member(db, hh.id, "엄마", Role.CO_ADMIN)

        # Demo login: dad@example.com / password1234
        _upsert_user(db, "dad@example.com", "password1234", dad.id)

        kb = _upsert_account(db, hh, dad, "kb_kookmin", "KB 급여통장")
        kiwoom = _upsert_account(db, hh, dad, "kiwoom", "키움 위탁")
        nh = _upsert_account(db, hh, mom, "nh_invest", "NH 연금저축")
        upbit = _upsert_account(db, hh, dad, "upbit", "업비트")

        _upsert_asset(
            db, hh, None, AssetType.REAL_ESTATE, "서울 아파트",
            manual_value=Decimal("1500000000"),
            metadata={"region_code": "11680"},
        )
        _upsert_asset(
            db, hh, kb, AssetType.CASH, "KB 급여통장 잔액",
            manual_value=Decimal("8500000"),
        )
        _upsert_asset(
            db, hh, kiwoom, AssetType.STOCK, "삼성전자",
            symbol="005930", quantity=Decimal("30"), cost_basis_avg=Decimal("68000"),
            valuation_source=ValuationSource.DAILY,
        )
        _upsert_asset(
            db, hh, nh, AssetType.ETF, "KODEX 200",
            symbol="069500", quantity=Decimal("200"), cost_basis_avg=Decimal("32000"),
            valuation_source=ValuationSource.DAILY,
        )
        _upsert_asset(
            db, hh, upbit, AssetType.CRYPTO, "BTC",
            symbol="KRW-BTC", quantity=Decimal("0.15"),
            valuation_source=ValuationSource.REALTIME,
        )
        _upsert_asset(
            db, hh, None, AssetType.GOLD_PHYSICAL, "현물 금(100g)",
            symbol="GOLD-PHYS", quantity=Decimal("100"),
            valuation_source=ValuationSource.DAILY,
        )

        # Seed price quotes so dashboard isn't all zeros offline
        _upsert_quote(db, "STOCK:005930", date.today(), Decimal("85000"), "krx")
        _upsert_quote(db, "STOCK:069500", date.today(), Decimal("35000"), "krx")
        _upsert_quote(db, "CRYPTO:KRW-BTC", date.today(), Decimal("95000000"), "upbit")
        _upsert_quote(db, "GOLD:KRX", date.today(), Decimal("140000"), "krx_gold")
        _upsert_quote(db, "FX:USD/KRW", date.today(), Decimal("1400"), "ecos_fx")

        # Liability
        existing = db.scalar(
            select(Liability).where(Liability.household_id == hh.id,
                                    Liability.label == "주택담보대출")
        )
        if existing is None:
            db.add(
                Liability(
                    household_id=hh.id,
                    owner_member_id=dad.id,
                    institution_code="kb_kookmin",
                    liability_type=LiabilityType.MORTGAGE,
                    label="주택담보대출",
                    principal=Decimal("500000000"),
                    balance=Decimal("380000000"),
                    interest_rate=Decimal("0.042"),
                    rate_type=RateType.FLOAT,
                    start_date=date(2022, 3, 1),
                    maturity_date=date(2052, 3, 1),
                )
            )

        # Cash flow: last month salary + card charge
        today = date.today()
        db.add(
            CashFlowEvent(
                household_id=hh.id, member_id=dad.id, event_date=today,
                kind=CashFlowKind.INCOME, category="salary",
                amount=Decimal("8000000"), counterparty="회사",
            )
        )
        db.add(
            CashFlowEvent(
                household_id=hh.id, member_id=dad.id, event_date=today,
                kind=CashFlowKind.CARD_CHARGE, category="card",
                amount=Decimal("3500000"), counterparty="KB카드",
            )
        )

        db.commit()
        print(f"✓ seeded household id={hh.id} with 6 assets + 1 liability")
        print("  login: dad@example.com / password1234")


def _upsert_user(db, email: str, password: str, member_id: int) -> User:
    u = db.scalar(select(User).where(User.email == email))
    if u is None:
        u = User(email=email, password_hash=hash_password(password), member_id=member_id)
        db.add(u)
        db.flush()
    return u


def _upsert_member(db, household_id: int, name: str, role: Role) -> Member:
    m = db.scalar(
        select(Member).where(Member.household_id == household_id, Member.name == name)
    )
    if m is None:
        m = Member(household_id=household_id, name=name, role=role)
        db.add(m)
        db.flush()
    return m


def _upsert_account(
    db, hh: Household, owner: Member, institution_code: str, account_name: str
) -> Account:
    a = db.scalar(
        select(Account).where(
            Account.household_id == hh.id, Account.account_name == account_name
        )
    )
    if a is None:
        a = Account(
            household_id=hh.id,
            owner_member_id=owner.id,
            institution_code=institution_code,
            account_name=account_name,
        )
        db.add(a)
        db.flush()
    return a


def _upsert_asset(
    db,
    hh: Household,
    account: Account | None,
    asset_type: AssetType,
    label: str,
    **kwargs,
) -> Asset:
    a = db.scalar(
        select(Asset).where(Asset.household_id == hh.id, Asset.label == label)
    )
    if a is not None:
        return a
    md = kwargs.pop("metadata", None)
    a = Asset(
        household_id=hh.id,
        account_id=account.id if account else None,
        asset_type=asset_type,
        label=label,
        asset_metadata=md,
        **kwargs,
    )
    db.add(a)
    db.flush()
    return a


def _upsert_quote(db, asset_key: str, quote_date: date, price: Decimal, source: str) -> None:
    existing = db.scalar(
        select(PriceQuote).where(
            PriceQuote.asset_key == asset_key,
            PriceQuote.quote_date == quote_date,
            PriceQuote.source == source,
        )
    )
    if existing is not None:
        return
    db.add(
        PriceQuote(
            asset_key=asset_key,
            quote_date=quote_date,
            price=price,
            currency="KRW",
            source=source,
        )
    )


if __name__ == "__main__":
    main()
