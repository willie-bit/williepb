"""Adapter-layer tests that don't hit the network."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from app.integrations.banks.kb_kookmin import KBKookminBankAdapter
from app.integrations.banks.woori import WooriBankAdapter
from app.integrations.registry import AdapterRegistry
from app.integrations.securities.kiwoom import KiwoomAdapter
from app.integrations.securities.nh_invest import NHInvestAdapter


def test_registry_resolves_registered_adapters():
    reg = AdapterRegistry()
    kb = KBKookminBankAdapter()
    reg.register_account(kb)
    assert reg.account("kb_kookmin") is kb
    assert reg.account("unknown") is None


def test_kb_csv_parsing(tmp_path: Path):
    csv = tmp_path / "kb.csv"
    csv.write_text(
        "계좌번호,계좌별칭,잔액,통화,기준일\n"
        "123-45-6789,월급통장,\"12,345,678\",KRW,2026-04-20\n"
        "555-66-7777,외화예금,1500.00,USD,2026.04.20\n",
        encoding="utf-8-sig",
    )
    out = KBKookminBankAdapter().fetch_balances({"csv_path": str(csv)})
    assert len(out) == 2
    assert out[0].balance == Decimal("12345678")
    assert out[0].currency == "KRW"
    assert out[0].as_of == date(2026, 4, 20)
    assert out[1].currency == "USD"


def test_woori_csv_parsing(tmp_path: Path):
    csv = tmp_path / "woori.csv"
    csv.write_text(
        "계좌번호,상품명,잔액,통화,기준일자\n"
        "1002-123-456,우리 WON 통장,3000000,KRW,20260420\n",
        encoding="utf-8-sig",
    )
    out = WooriBankAdapter().fetch_balances({"csv_path": str(csv)})
    assert len(out) == 1
    assert out[0].balance == Decimal("3000000")
    assert out[0].as_of == date(2026, 4, 20)


def test_kiwoom_csv_parsing(tmp_path: Path):
    csv = tmp_path / "kiwoom.csv"
    csv.write_text(
        "계좌번호,종목코드,종목명,보유수량,매입평균가,기준일자\n"
        "8888-1,005930,삼성전자,10,70000,2026-04-20\n"
        "8888-1,373220,LG에너지솔루션,2,400000,2026-04-20\n",
        encoding="utf-8-sig",
    )
    holdings = KiwoomAdapter().fetch_holdings({"csv_path": str(csv)})
    assert len(holdings) == 2
    assert holdings[0].symbol == "005930"
    assert holdings[0].quantity == Decimal("10")
    assert holdings[0].cost_basis_avg == Decimal("70000")
    assert holdings[0].institution_code == "kiwoom"


def test_nh_csv_parsing(tmp_path: Path):
    csv = tmp_path / "nh.csv"
    csv.write_text(
        "계좌번호,종목코드,종목명,잔고수량,매입단가,조회일자\n"
        "11-1,069500,KODEX 200,50,30000,2026-04-20\n",
        encoding="utf-8-sig",
    )
    holdings = NHInvestAdapter().fetch_holdings({"csv_path": str(csv)})
    assert holdings[0].symbol == "069500"
    assert holdings[0].quantity == Decimal("50")
    assert holdings[0].institution_code == "nh_invest"


def test_empty_credentials_returns_empty():
    assert KBKookminBankAdapter().fetch_balances({}) == []
    assert KiwoomAdapter().fetch_holdings({}) == []
