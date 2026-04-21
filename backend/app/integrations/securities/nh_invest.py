"""NH투자증권 adapter.

Real integration paths:

1. **NH투자증권 Open API / 나무증권 API**: OAuth 토큰 방식.
   AppKey/AppSecret → access_token → 잔고조회 엔드포인트. docs: api.nhqv.com.
2. **CSV 업로드 (MVP)**: 나무 HTS/MTS 잔고 → 엑셀 다운로드.
"""

from __future__ import annotations

from pathlib import Path

from app.integrations.base import BalanceSnapshot, HoldingSnapshot
from app.integrations.securities._csv import HoldingCsvColumns, parse_holdings_csv


class NHInvestAdapter:
    institution_code = "nh_invest"
    display_name = "NH투자증권"

    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]:
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
                quantity="잔고수량",
                cost_basis_avg="매입단가",
                currency=None,
                account_id="계좌번호",
                as_of="조회일자",
            ),
            default_account_id=credentials.get("default_account_id", ""),
        )
