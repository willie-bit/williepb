"""Central lookup of adapters by institution / market / real-estate source.

Adapters register themselves via `register_*` calls in their module top-level;
import those modules once (see `app.integrations.bootstrap`) and the registry
is populated. The API layer resolves adapters by string code so new providers
can be added by dropping in a module and importing it.
"""

from __future__ import annotations

from functools import lru_cache

from app.integrations.base import AccountAdapter, MarketQuoteAdapter, RealEstateAdapter


class AdapterRegistry:
    def __init__(self) -> None:
        self._accounts: dict[str, AccountAdapter] = {}
        self._markets: dict[str, MarketQuoteAdapter] = {}
        self._realestate: dict[str, RealEstateAdapter] = {}

    def register_account(self, adapter: AccountAdapter) -> None:
        self._accounts[adapter.institution_code] = adapter

    def register_market(self, adapter: MarketQuoteAdapter) -> None:
        self._markets[adapter.source] = adapter

    def register_realestate(self, adapter: RealEstateAdapter) -> None:
        self._realestate[adapter.source] = adapter

    def account(self, code: str) -> AccountAdapter | None:
        return self._accounts.get(code)

    def market(self, source: str) -> MarketQuoteAdapter | None:
        return self._markets.get(source)

    def realestate(self, source: str) -> RealEstateAdapter | None:
        return self._realestate.get(source)

    def list_accounts(self) -> list[str]:
        return sorted(self._accounts.keys())

    def list_markets(self) -> list[str]:
        return sorted(self._markets.keys())

    def list_realestate(self) -> list[str]:
        return sorted(self._realestate.keys())


@lru_cache(maxsize=1)
def get_registry() -> AdapterRegistry:
    from app.integrations import bootstrap  # noqa: F401 — side effect: populates registry

    return bootstrap.registry
