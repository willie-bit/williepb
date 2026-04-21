"""키움증권 adapter.

Real integration paths:

1. **키움 OpenAPI+ (COM/OCX, Windows 전용)**: the legacy offering; auth via
   PyKiwoom on a Windows host. 운영 부담이 커서 MVP에선 채택하지 않는다.

2. **키움 REST/WebSocket OpenAPI (베타)**: 발급받은 AppKey/AppSecret으로 OAuth
   토큰을 교환 후 본인 위탁계좌 잔고/거래내역 조회 가능. docs: openapi.kiwoom.com.

3. **CSV 업로드 (MVP 기본)**: 영웅문S/Global → 잔고 → 엑셀 다운로드.

이 어댑터는 (3)을 구현하고 (2)는 TODO로 남긴다.
"""

from __future__ import annotations

from pathlib import Path

from app.integrations.base import BalanceSnapshot, HoldingSnapshot
from app.integrations.securities._csv import HoldingCsvColumns, parse_holdings_csv


class KiwoomAdapter:
    institution_code = "kiwoom"
    display_name = "키움증권"

    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]:
        # 증권사는 예수금을 원화 잔액으로 별도 제공. MVP는 홀딩만 취급하고
        # 예수금은 CASH 자산으로 사용자가 직접 등록하도록 한다.
        return []

    def fetch_holdings(self, credentials: dict) -> list[HoldingSnapshot]:
        csv_path = credentials.get("csv_path")
        if not csv_path:
            return []
        return parse_holdings_csv(
            Path(csv_path),
            institution_code=self.institution_code,
            columns=HoldingCsvColumns(
                symbol="종목코드",
                label="종목명",
                quantity="보유수량",
                cost_basis_avg="매입평균가",
                currency=None,  # 국내주식 전제; 해외주식 CSV면 헤더에 통화 컬럼이 있어야 함
                account_id="계좌번호",
                as_of="기준일자",
            ),
            default_account_id=credentials.get("default_account_id", ""),
        )
