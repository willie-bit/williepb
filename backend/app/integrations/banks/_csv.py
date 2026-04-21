"""Shared CSV-import fallback for bank adapters.

Users can export their account activity from the bank app and drop the file into
`imports/<institution>/`. The CSV schema is institution-specific and kept in each
adapter, but the reader + parsing utilities live here to avoid duplication.
"""

from __future__ import annotations

import csv
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8-sig", newline="") as f:
        return [dict(row) for row in csv.DictReader(f)]


def parse_amount(raw: str) -> Decimal:
    cleaned = (raw or "0").replace(",", "").replace("원", "").strip()
    return Decimal(cleaned or "0")


def parse_kdate(raw: str) -> date | None:
    for fmt in ("%Y-%m-%d", "%Y.%m.%d", "%Y/%m/%d", "%Y%m%d"):
        try:
            return datetime.strptime(raw.strip(), fmt).date()
        except (ValueError, AttributeError):
            continue
    return None
