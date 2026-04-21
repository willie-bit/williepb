"""Shared holding-CSV parser for brokerage adapters.

Securities apps (키움/NH/한투) 모두 `잔고조회 → 엑셀/CSV 다운로드` 기능을 제공한다.
헤더만 맵핑해 주면 공통 리더로 처리된다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.integrations.banks._csv import parse_amount, parse_kdate, read_csv_rows
from app.integrations.base import HoldingSnapshot


@dataclass(slots=True)
class HoldingCsvColumns:
    """Column-name mapping for a given brokerage's balance CSV."""

    symbol: str
    label: str
    quantity: str
    cost_basis_avg: str | None = None
    currency: str | None = None
    account_id: str | None = None
    as_of: str | None = None


def parse_holdings_csv(
    path: Path,
    institution_code: str,
    columns: HoldingCsvColumns,
    default_account_id: str = "",
) -> list[HoldingSnapshot]:
    out: list[HoldingSnapshot] = []
    for row in read_csv_rows(path):
        symbol = (row.get(columns.symbol) or "").strip()
        qty_raw = row.get(columns.quantity, "0")
        if not symbol or not qty_raw:
            continue
        qty = parse_amount(qty_raw)
        if qty == Decimal("0"):
            continue
        cost = (
            parse_amount(row.get(columns.cost_basis_avg, "0"))
            if columns.cost_basis_avg
            else None
        )
        out.append(
            HoldingSnapshot(
                institution_code=institution_code,
                external_account_id=(
                    row.get(columns.account_id, "").strip()
                    if columns.account_id
                    else default_account_id
                ),
                symbol=symbol,
                label=(row.get(columns.label) or symbol).strip(),
                quantity=qty,
                cost_basis_avg=cost,
                currency=(
                    (row.get(columns.currency) or "KRW").strip()
                    if columns.currency
                    else "KRW"
                ),
                as_of=(
                    parse_kdate(row.get(columns.as_of, "")) if columns.as_of else None
                )
                or date.today(),
                raw=row,
            )
        )
    return out
