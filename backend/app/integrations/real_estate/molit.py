"""국토교통부 실거래가 어댑터 (공공데이터포털).

단지 평균가 참고용. 부동산원 지수와 조합해 "사용자 감정가 × 지수변동률"로
현재가를 산출하되, 거래가 있는 단지는 실거래가 평균으로 보정한다.

MVP에선 키 미설정/호출 실패 시 None을 반환 (valuation 서비스가 폴백 처리).
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.core.config import get_settings
from app.integrations.base import RealEstateQuote


class MOLITAdapter:
    source = "molit_trade"
    display_name = "국토부 실거래가"

    def __init__(self, api_key: str | None = None, timeout: float = 5.0) -> None:
        self._api_key = api_key or get_settings().molit_api_key
        self._timeout = timeout

    def fetch_valuation(self, identifier: str, on_date: date) -> RealEstateQuote | None:
        """`identifier` = "<법정동코드>:<단지명>".

        TODO: 실제 XML 응답 파싱. 현재는 키 검사만 수행하고 None 폴백.
        """
        if not self._api_key:
            return None
        # placeholder; real impl will call 아파트매매 실거래가 상세자료 endpoint.
        return RealEstateQuote(
            identifier=identifier,
            quote_date=on_date,
            value=Decimal("0"),
            currency="KRW",
            source=self.source,
            metadata={"note": "TODO: 실거래가 평균 계산 미구현"},
        )
