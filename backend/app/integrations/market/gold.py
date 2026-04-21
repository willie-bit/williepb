"""금 시세 어댑터 (KRX 금시장).

KRX 금시장 코드: `04020000` — 한국거래소 "KRX금시장" 고시가.
pykrx 미사용 환경에서는 사용자가 수동 입력하거나 한국금거래소 공시가를
CSV로 업로드할 수 있도록 `manual_value` 를 지원한다 (asset.manual_value).

금 ETF/펀드(금융상품)는 KRXAdapter로 커버된다 (예: 411060 KODEX 골드선물(H)).
따라서 여기선 **현물 g당 시세**만 취급한다.
"""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from app.integrations.base import MarketQuote

KRX_GOLD_SYMBOL = "04020000"


class KRXGoldAdapter:
    source = "krx_gold"
    display_name = "KRX 금시장"

    def fetch_quotes(self, symbols: list[str], on_date: date) -> list[MarketQuote]:
        """`symbols`는 무시하고 고정 심볼의 시세만 반환한다.

        반환 `asset_key`는 `GOLD:KRX` 로 통일한다 — 사용자의 금 자산은 현물/ETF 구분 없이
        집계 단계에서 `GOLD_PHYSICAL` / `GOLD_FINANCIAL`로 분리 조회한다.
        """
        try:
            from pykrx import stock  # type: ignore
        except ImportError:
            return []
        # 주말·휴장 보정: 최근 7일 범위에서 마지막 종가를 사용
        start = (on_date - timedelta(days=7)).strftime("%Y%m%d")
        end = on_date.strftime("%Y%m%d")
        try:
            df = stock.get_market_ohlcv_by_date(start, end, KRX_GOLD_SYMBOL)
        except Exception:
            return []
        if df is None or df.empty:
            return []
        close = df["종가"].iloc[-1]
        return [
            MarketQuote(
                asset_key="GOLD:KRX",
                quote_date=on_date,
                price=Decimal(str(close)),
                currency="KRW",
                source="krx_gold",
            )
        ]
