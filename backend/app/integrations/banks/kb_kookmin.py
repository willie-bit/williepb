"""KB국민은행 adapter.

Real integration path (two viable routes, to be picked post-MVP):

1. **마이데이터 중계 사업자**: partner with a licensed 마이데이터 사업자
   (e.g. 뱅크샐러드, 토스, 네이버페이). They expose aggregated bank data
   through an OAuth-like consent flow — user links their KB account, we store
   the `access_token` / `member_id` returned by the broker, and call their
   generic "accounts/balances" endpoint. No direct KB endpoint needed.

2. **오픈뱅킹 (금융결제원)**: direct registration at developers.open-banking.or.kr
   gives personal-use API access to KRW balances/transactions for the user's
   own accounts. 증빙 서류와 심사 필요. Token expiry handling required.

Until either path lands, this adapter accepts a CSV export from the KB STAR app
(`잔액조회 → 내역 다운로드`) and returns it as BalanceSnapshots.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.integrations.banks._csv import parse_amount, parse_kdate, read_csv_rows
from app.integrations.base import BalanceSnapshot, HoldingSnapshot


class KBKookminBankAdapter:
    institution_code = "kb_kookmin"
    display_name = "KB국민은행"

    def fetch_balances(self, credentials: dict) -> list[BalanceSnapshot]:
        csv_path = credentials.get("csv_path")
        if not csv_path:
            return []
        return _parse_kb_balance_csv(Path(csv_path))

    def fetch_holdings(self, credentials: dict) -> list[HoldingSnapshot]:
        # 은행 계좌에는 원화/외화 잔액만 있음 (예·적금·수시). 홀딩은 증권사 측에서 취급.
        return []


def _parse_kb_balance_csv(path: Path) -> list[BalanceSnapshot]:
    """Expected columns (KB STAR 내역 다운로드, 한국어 헤더):
    계좌번호, 계좌별칭, 잔액, 통화, 기준일
    """
    out: list[BalanceSnapshot] = []
    for row in read_csv_rows(path):
        balance = parse_amount(row.get("잔액", "0"))
        if balance == Decimal("0") and not row.get("잔액"):
            continue
        out.append(
            BalanceSnapshot(
                institution_code="kb_kookmin",
                external_account_id=(row.get("계좌번호") or "").strip(),
                account_name=(row.get("계좌별칭") or row.get("계좌번호") or "KB 계좌").strip(),
                balance=balance,
                currency=(row.get("통화") or "KRW").strip() or "KRW",
                as_of=parse_kdate(row.get("기준일", "")) or date.today(),
            )
        )
    return out
