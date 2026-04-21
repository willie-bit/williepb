"""우리은행 adapter.

Real-integration notes mirror KB국민: MyData broker or 금융결제원 오픈뱅킹.
우리은행 자체 개인 API는 없다. MVP는 CSV 업로드로 시작한다.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.integrations.banks._csv import parse_amount, parse_kdate, read_csv_rows
from app.integrations.base import BalanceSnapshot, HoldingSnapshot


class WooriBankAdapter:
    institution_code = "woori"
    display_name = "우리은행"

    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]:
        csv_path = credentials.get("csv_path")
        if not csv_path:
            return []
        return _parse_woori_balance_csv(Path(csv_path))

    def fetch_holdings(self, credentials: dict) -> list[HoldingSnapshot]:
        return []


def _parse_woori_balance_csv(path: Path) -> list[BalanceSnapshot]:
    """Expected columns: 계좌번호, 상품명, 잔액, 통화, 기준일자"""
    out: list[BalanceSnapshot] = []
    for row in read_csv_rows(path):
        balance = parse_amount(row.get("잔액", "0"))
        if balance == Decimal("0") and not row.get("잔액"):
            continue
        out.append(
            BalanceSnapshot(
                institution_code="woori",
                external_account_id=(row.get("계좌번호") or "").strip(),
                account_name=(row.get("상품명") or "우리은행 계좌").strip(),
                balance=balance,
                currency=(row.get("통화") or "KRW").strip() or "KRW",
                as_of=parse_kdate(row.get("기준일자", "")) or date.today(),
            )
        )
    return out
