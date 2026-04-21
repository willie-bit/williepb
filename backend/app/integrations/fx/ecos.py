"""한국은행 ECOS 환율 어댑터.

ECOS OpenAPI: https://ecos.bok.or.kr/api
통계표코드 731Y001 (일별 시장평균환율), 품목 `0000001` = USD/KRW.

symbols는 "USD/KRW", "EUR/KRW" 등 `{base}/KRW` 형태만 지원한다 (MVP).
API key가 비어있으면 빈 결과 — 호출자는 마지막 저장치로 폴백한다.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import httpx

from app.core.config import get_settings
from app.integrations.base import MarketQuote

_BASE = "https://ecos.bok.or.kr/api/StatisticSearch"
_TABLE = "731Y001"  # 일별 시장평균환율/재정환율

# (base currency → ECOS item code)
_ITEM_BY_BASE = {
    "USD": "0000001",
    "JPY": "0000002",  # 100엔당
    "EUR": "0000003",
    "CNY": "0000053",
}


class ECOSFxAdapter:
    source = "ecos_fx"
    display_name = "한국은행 ECOS 환율"

    def __init__(self, api_key: str | None = None, timeout: float = 5.0) -> None:
        self._api_key = api_key or get_settings().ecos_api_key
        self._timeout = timeout

    def fetch_quotes(self, symbols: list[str], on_date: date) -> list[MarketQuote]:
        if not self._api_key or not symbols:
            return []
        out: list[MarketQuote] = []
        day_str = on_date.strftime("%Y%m%d")
        for pair in symbols:
            base, quote = _parse_pair(pair)
            item = _ITEM_BY_BASE.get(base)
            if not item or quote != "KRW":
                continue
            url = (
                f"{_BASE}/{self._api_key}/json/kr/1/1/{_TABLE}/D/{day_str}/{day_str}/{item}"
            )
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    resp = client.get(url)
                    resp.raise_for_status()
                    data = resp.json()
            except httpx.HTTPError:
                continue
            rows = data.get("StatisticSearch", {}).get("row", [])
            if not rows:
                continue
            value = Decimal(str(rows[0]["DATA_VALUE"]))
            if base == "JPY":
                value = value / Decimal("100")  # ECOS는 100엔 단위 공시
            out.append(
                MarketQuote(
                    asset_key=f"FX:{base}/KRW",
                    quote_date=on_date,
                    price=value,
                    currency="KRW",
                    source="ecos_fx",
                )
            )
        return out


def _parse_pair(pair: str) -> tuple[str, str]:
    if "/" in pair:
        base, quote = pair.split("/", 1)
        return base.upper(), quote.upper()
    return pair.upper(), "KRW"
