"""한국부동산원 R-ONE 지수 어댑터.

MVP 정책: KB시세 대신 **부동산원 주택가격동향조사(월간)** 지수를 사용한다.
- 각 자산(asset)의 metadata에 base_appraisal(사용자 최초 감정가)과
  region_code(시군구 코드)를 기록한다.
- 최신 지수를 가져와 base 대비 변동률로 현재가를 산출한다:
      current_value = base_appraisal × (latest_index / base_index)

실 API 엔드포인트/통계표는 R-ONE(realestatestats.reb.or.kr) 요청 후 확정.
키가 비었거나 호출 실패 시 None을 반환 → valuation 서비스가 최근 스냅샷으로 폴백.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

import httpx

from app.core.config import get_settings
from app.integrations.base import RealEstateQuote


@dataclass(slots=True)
class IndexPoint:
    year_month: str  # "YYYY-MM"
    value: Decimal


class REBIndexAdapter:
    source = "reb_index"
    display_name = "한국부동산원 지수"

    def __init__(self, api_key: str | None = None, timeout: float = 5.0) -> None:
        self._api_key = api_key or get_settings().reb_api_key
        self._timeout = timeout

    def fetch_valuation(self, identifier: str, on_date: date) -> RealEstateQuote | None:
        """`identifier` = "<region_code>:<base_ym>:<base_appraisal>"

        예: "11680:2024-01:1500000000"  → 서울 강남구, 2024년 1월 기준가 15억.
        """
        try:
            region, base_ym, base_val = identifier.split(":")
            base_value = Decimal(base_val)
        except (ValueError, ArithmeticError):
            return None

        if not self._api_key:
            return None

        try:
            base_idx = self._fetch_index(region, base_ym)
            latest = self._fetch_latest_index(region, on_date)
        except httpx.HTTPError:
            return None
        if base_idx is None or latest is None or base_idx.value == 0:
            return None

        current = (base_value * latest.value / base_idx.value).quantize(Decimal("1"))
        return RealEstateQuote(
            identifier=identifier,
            quote_date=on_date,
            value=current,
            currency="KRW",
            source=self.source,
            metadata={
                "base_index": str(base_idx.value),
                "latest_index": str(latest.value),
                "latest_ym": latest.year_month,
                "region_code": region,
            },
        )

    # --- internal ---
    def _fetch_index(self, region_code: str, year_month: str) -> IndexPoint | None:
        # TODO: replace with real R-ONE endpoint once the statistical table is chosen.
        # Shape is intentionally minimal so unit tests can patch this.
        return None

    def _fetch_latest_index(self, region_code: str, on_date: date) -> IndexPoint | None:
        return None
