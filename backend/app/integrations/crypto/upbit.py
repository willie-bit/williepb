"""Upbit adapter — both AccountAdapter (holdings) and MarketQuoteAdapter (prices).

Endpoints used (docs.upbit.com):
- GET /v1/accounts              (requires JWT with access_key/secret_key)
- GET /v1/ticker?markets=...    (public)

Network/auth failures raise; the caller decides whether to degrade to last-known
quotes. Empty credentials silently yield an empty holdings list (unconfigured).
"""

from __future__ import annotations

import hashlib
import time
import urllib.parse
import uuid
from datetime import date
from decimal import Decimal

import httpx

from app.integrations.base import BalanceSnapshot, HoldingSnapshot, MarketQuote

_BASE = "https://api.upbit.com"


class UpbitAdapter:
    institution_code = "upbit"
    source = "upbit"
    display_name = "업비트"

    def __init__(self, timeout: float = 5.0) -> None:
        self._timeout = timeout

    # --- AccountAdapter ---
    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]:
        # Upbit은 KRW 예치금과 코인 잔고를 같은 응답으로 반환한다.
        # KRW 예치금만 BalanceSnapshot, 코인은 fetch_holdings로 분리한다.
        rows = self._fetch_accounts(credentials)
        out: list[BalanceSnapshot] = []
        for r in rows:
            if r.get("currency") == "KRW":
                out.append(
                    BalanceSnapshot(
                        institution_code="upbit",
                        external_account_id="upbit",
                        account_name="업비트 원화",
                        balance=Decimal(str(r.get("balance", "0"))),
                        currency="KRW",
                        as_of=date.today(),
                    )
                )
        return out

    def fetch_holdings(self, credentials: dict) -> list[HoldingSnapshot]:
        rows = self._fetch_accounts(credentials)
        out: list[HoldingSnapshot] = []
        for r in rows:
            cur = r.get("currency")
            if not cur or cur == "KRW":
                continue
            qty = Decimal(str(r.get("balance", "0"))) + Decimal(str(r.get("locked", "0")))
            if qty == 0:
                continue
            avg = r.get("avg_buy_price")
            out.append(
                HoldingSnapshot(
                    institution_code="upbit",
                    external_account_id="upbit",
                    symbol=f"KRW-{cur}",
                    label=cur,
                    quantity=qty,
                    cost_basis_avg=Decimal(str(avg)) if avg else None,
                    currency=r.get("unit_currency") or "KRW",
                    as_of=date.today(),
                    raw=r,
                )
            )
        return out

    # --- MarketQuoteAdapter ---
    def fetch_quotes(self, symbols: list[str], on_date: date) -> list[MarketQuote]:
        if not symbols:
            return []
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(f"{_BASE}/v1/ticker", params={"markets": ",".join(symbols)})
            resp.raise_for_status()
            data = resp.json()
        out: list[MarketQuote] = []
        for row in data:
            out.append(
                MarketQuote(
                    asset_key=f"CRYPTO:{row['market']}",
                    quote_date=on_date,
                    price=Decimal(str(row["trade_price"])),
                    currency="KRW" if row["market"].startswith("KRW-") else "USDT",
                    source="upbit",
                )
            )
        return out

    # --- internal ---
    def _fetch_accounts(self, credentials: dict) -> list[dict]:
        access = credentials.get("access_key") or ""
        secret = credentials.get("secret_key") or ""
        if not access or not secret:
            return []
        try:
            import jwt  # type: ignore
        except Exception as exc:  # broken PyJWT / crypto stack
            raise RuntimeError(
                "PyJWT not usable; `pip install pyjwt cryptography` to use real Upbit auth"
            ) from exc
        payload = {"access_key": access, "nonce": str(uuid.uuid4())}
        token = jwt.encode(payload, secret, algorithm="HS256")
        headers = {"Authorization": f"Bearer {token}"}
        with httpx.Client(timeout=self._timeout) as client:
            resp = client.get(f"{_BASE}/v1/accounts", headers=headers)
            resp.raise_for_status()
            return resp.json()

    # helper used in tests to avoid network; kept here to document the signing flow
    @staticmethod
    def _query_hash(query: dict) -> str:
        q = urllib.parse.urlencode(query)
        h = hashlib.sha512()
        h.update(q.encode())
        return h.hexdigest()

    # kept to silence unused-import linters in minimal envs
    _t = staticmethod(time.time)
