"""KRX 시세 어댑터.

MVP에서는 `pykrx` 를 선택적 의존성으로 사용한다 (`pip install williepb-backend[market]`).
pykrx는 KRX 공개 페이지를 크롤링하는 라이브러리로, 정식 상용 사용 시
라이선스/접근 제약을 검토해야 한다. 대안: 한국투자증권 OpenAPI의 시세 엔드포인트.

pykrx 미설치 또는 네트워크 장애 시 빈 리스트를 반환해 배치가 실패하지 않도록 한다.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from app.integrations.base import MarketQuote


class KRXAdapter:
    source = "krx"
    display_name = "KRX (pykrx)"

    def fetch_quotes(self, symbols: list[str], on_date: date) -> list[MarketQuote]:
        if not symbols:
            return []
        try:
            from pykrx import stock  # type: ignore
        except ImportError:
            return []
        out: list[MarketQuote] = []
        day_str = on_date.strftime("%Y%m%d")
        for sym in symbols:
            try:
                df = stock.get_market_ohlcv_by_date(day_str, day_str, sym)
            except Exception:
                continue
            if df is None or df.empty:
                continue
            close = df["종가"].iloc[-1]
            out.append(
                MarketQuote(
                    asset_key=f"STOCK:{sym}",
                    quote_date=on_date,
                    price=Decimal(str(close)),
                    currency="KRW",
                    source="krx",
                )
            )
        return out
