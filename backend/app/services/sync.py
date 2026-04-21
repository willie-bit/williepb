"""Sync orchestration — pulls prices and account holdings via the adapter registry.

Kept deliberately small: each phase is a standalone function so a Celery/Airflow
DAG later can parallelize the steps without having to refactor business logic.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.integrations import get_registry
from app.integrations.base import MarketQuoteAdapter
from app.models import Asset, AssetType, PriceQuote


@dataclass(slots=True)
class SyncReport:
    prices_written: int = 0
    accounts_synced: int = 0
    errors: list[str] = field(default_factory=list)


def _symbols_needed(db: Session, household_id: int | None) -> dict[str, list[str]]:
    """Group symbols by the adapter source to call.

    Returns {source: [symbol, ...]}. Asset→source mapping:
      STOCK/ETF/GOLD_FINANCIAL → krx (국내 심볼 전제; 해외는 추후 확장)
      CRYPTO → upbit
      GOLD_PHYSICAL → krx_gold (symbols 무시)
    """
    stmt = select(Asset).where(Asset.symbol.is_not(None))
    if household_id is not None:
        stmt = stmt.where(Asset.household_id == household_id)
    assets = db.scalars(stmt).all()

    out: dict[str, list[str]] = {"krx": [], "upbit": [], "krx_gold": []}
    for a in assets:
        if a.asset_type in (AssetType.STOCK, AssetType.ETF, AssetType.GOLD_FINANCIAL):
            out["krx"].append(a.symbol)
        elif a.asset_type == AssetType.CRYPTO:
            out["upbit"].append(a.symbol)
        elif a.asset_type == AssetType.GOLD_PHYSICAL:
            out["krx_gold"].append("")  # sentinel — adapter ignores
    # dedupe
    return {k: sorted(set(v)) for k, v in out.items() if v}


def sync_prices(db: Session, on_date: date, household_id: int | None = None) -> SyncReport:
    report = SyncReport()
    registry = get_registry()
    by_source = _symbols_needed(db, household_id)

    for source, symbols in by_source.items():
        adapter: MarketQuoteAdapter | None = registry.market(source)
        if adapter is None:
            report.errors.append(f"no adapter for {source}")
            continue
        try:
            quotes = adapter.fetch_quotes(symbols, on_date)
        except Exception as exc:  # keep the pipeline alive on provider outages
            report.errors.append(f"{source}: {exc}")
            continue
        for q in quotes:
            row = PriceQuote(
                asset_key=q.asset_key,
                quote_date=q.quote_date,
                price=Decimal(str(q.price)),
                currency=q.currency,
                source=q.source or source,
            )
            # uniqueness via (asset_key, quote_date, source) — upsert-ish logic:
            existing = db.scalar(
                select(PriceQuote).where(
                    PriceQuote.asset_key == row.asset_key,
                    PriceQuote.quote_date == row.quote_date,
                    PriceQuote.source == row.source,
                )
            )
            if existing:
                existing.price = row.price
                existing.currency = row.currency
            else:
                db.add(row)
            report.prices_written += 1

    db.flush()
    return report


def sync_account(
    db: Session, account_id: int, credentials: dict
) -> SyncReport:
    """Pull holdings for a given account and upsert matching Asset rows.

    Matching key: (account_id, symbol). Unknown symbols create a new Asset
    with `valuation_source=DAILY` so the next price sync will populate them.
    """
    from app.models import Account, ValuationSource

    report = SyncReport()
    registry = get_registry()
    account = db.get(Account, account_id)
    if account is None:
        report.errors.append(f"account {account_id} not found")
        return report
    adapter = registry.account(account.institution_code)
    if adapter is None:
        report.errors.append(f"no adapter for {account.institution_code}")
        return report

    try:
        holdings = adapter.fetch_holdings(credentials)
    except Exception as exc:
        report.errors.append(f"{account.institution_code}: {exc}")
        return report

    existing = {
        (a.account_id, a.symbol): a
        for a in db.scalars(select(Asset).where(Asset.account_id == account_id)).all()
    }
    for h in holdings:
        key = (account_id, h.symbol)
        if key in existing:
            asset = existing[key]
            asset.quantity = h.quantity
            if h.cost_basis_avg is not None:
                asset.cost_basis_avg = h.cost_basis_avg
        else:
            asset_type = _guess_asset_type(h.symbol)
            asset = Asset(
                household_id=account.household_id,
                account_id=account_id,
                asset_type=asset_type,
                label=h.label,
                symbol=h.symbol,
                currency=h.currency,
                quantity=h.quantity,
                cost_basis_avg=h.cost_basis_avg,
                valuation_source=ValuationSource.DAILY,
            )
            db.add(asset)
        report.accounts_synced += 1
    db.flush()
    return report


def _guess_asset_type(symbol: str) -> AssetType:
    if symbol.startswith("KRW-") or "-" in symbol:
        return AssetType.CRYPTO
    # KRX 국내주식 코드는 6자리 숫자. ETF는 별도 구분이 어렵다 — 사용자가 추후 수정.
    return AssetType.STOCK
