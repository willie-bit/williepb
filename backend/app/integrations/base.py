"""Integration adapter contracts.

Three Protocols cover every external data source:

- AccountAdapter    : user-specific account/holding sync (banks, brokerages, crypto)
- MarketQuoteAdapter: symbol → price (KRX, Upbit, gold, FX)
- RealEstateAdapter : address/complex-code → valuation and/or price index

Adapters stay thin: they return dataclass DTOs and leave persistence to services.
Unimplemented sources raise NotImplementedError so the caller can fall back
to manual/CSV inputs without crashing the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Protocol, runtime_checkable


@dataclass(slots=True)
class BalanceSnapshot:
    institution_code: str
    external_account_id: str
    account_name: str
    balance: Decimal
    currency: str = "KRW"
    as_of: date | None = None


@dataclass(slots=True)
class HoldingSnapshot:
    institution_code: str
    external_account_id: str
    symbol: str
    label: str
    quantity: Decimal
    cost_basis_avg: Decimal | None = None
    currency: str = "KRW"
    as_of: date | None = None
    raw: dict = field(default_factory=dict)


@dataclass(slots=True)
class MarketQuote:
    asset_key: str
    quote_date: date
    price: Decimal
    currency: str = "KRW"
    source: str = ""


@dataclass(slots=True)
class RealEstateQuote:
    identifier: str  # 단지코드 or 주소 해시
    quote_date: date
    value: Decimal
    currency: str = "KRW"
    source: str = ""
    metadata: dict = field(default_factory=dict)


@runtime_checkable
class AccountAdapter(Protocol):
    """Pulls balances / holdings for a specific user account at an institution.

    Implementations typically need OAuth tokens or API keys, stored encrypted
    and passed in via `credentials`. Returning empty lists is valid (e.g. account
    exists but has no positions today).
    """

    institution_code: str

    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]: ...

    def fetch_holdings(self, credentials: dict) -> list[HoldingSnapshot]: ...


@runtime_checkable
class MarketQuoteAdapter(Protocol):
    source: str

    def fetch_quotes(self, symbols: list[str], on_date: date) -> list[MarketQuote]: ...


@runtime_checkable
class RealEstateAdapter(Protocol):
    source: str

    def fetch_valuation(self, identifier: str, on_date: date) -> RealEstateQuote | None: ...
