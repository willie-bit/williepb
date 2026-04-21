"""Asset valuation — turn quantity + latest price (+ FX) into a KRW value.

Rules:
- `manual_value` 가 있으면 그것을 사용 (부동산·차량·실물에 권장).
- 그 외엔 `PriceQuote`의 최신가 × quantity 로 계산.
- 자산 currency ≠ 가구 base_currency 인 경우 FX 시세(price_quote "FX:<ccy>/KRW")로 환산.
- 해당 가격이 없으면 0 으로 폴백하고 경고 플래그를 반환 (호출자가 대시보드에 표시 가능).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, AssetType, PriceQuote


@dataclass(slots=True)
class ValuedAsset:
    asset: Asset
    value: Decimal
    unit_price: Decimal | None
    source: str
    missing_price: bool = False


def _asset_key(asset: Asset) -> str | None:
    if not asset.symbol:
        return None
    prefix = {
        AssetType.STOCK: "STOCK",
        AssetType.ETF: "STOCK",
        AssetType.FUND: "FUND",
        AssetType.CRYPTO: "CRYPTO",
        AssetType.GOLD_PHYSICAL: "GOLD",
        AssetType.GOLD_FINANCIAL: "STOCK",
        AssetType.CASH: "FX",
    }.get(asset.asset_type)
    if prefix is None:
        return None
    return f"{prefix}:{asset.symbol}"


def _latest_quote(db: Session, asset_key: str, on_date: date) -> PriceQuote | None:
    stmt = (
        select(PriceQuote)
        .where(PriceQuote.asset_key == asset_key, PriceQuote.quote_date <= on_date)
        .order_by(PriceQuote.quote_date.desc(), PriceQuote.fetched_at.desc())
        .limit(1)
    )
    return db.scalars(stmt).first()


def _fx_to_base(
    db: Session, from_ccy: str, base_ccy: str, on_date: date
) -> Decimal | None:
    if from_ccy == base_ccy:
        return Decimal("1")
    q = _latest_quote(db, f"FX:{from_ccy}/{base_ccy}", on_date)
    return Decimal(str(q.price)) if q else None


def value_asset(db: Session, asset: Asset, on_date: date, base_ccy: str = "KRW") -> ValuedAsset:
    # Manual override wins.
    if asset.manual_value is not None:
        fx = _fx_to_base(db, asset.currency, base_ccy, on_date) or Decimal("1")
        return ValuedAsset(
            asset=asset,
            value=Decimal(str(asset.manual_value)) * fx,
            unit_price=None,
            source="manual",
        )

    key = _asset_key(asset)
    if key is None:
        return ValuedAsset(asset=asset, value=Decimal("0"), unit_price=None, source="none",
                           missing_price=True)

    quote = _latest_quote(db, key, on_date)
    if quote is None:
        return ValuedAsset(asset=asset, value=Decimal("0"), unit_price=None,
                           source="none", missing_price=True)

    fx = _fx_to_base(db, quote.currency, base_ccy, on_date)
    if fx is None:
        return ValuedAsset(
            asset=asset, value=Decimal("0"), unit_price=Decimal(str(quote.price)),
            source=quote.source, missing_price=True,
        )

    unit = Decimal(str(quote.price))
    qty = Decimal(str(asset.quantity or 0))
    return ValuedAsset(asset=asset, value=unit * qty * fx, unit_price=unit, source=quote.source)
