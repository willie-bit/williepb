"""양도소득세 계산기 (주택 양도, 단순화 버전).

⚠️ 1세대1주택 비과세(12억 이하)·다주택 중과·조정대상지역·실제거주요건 등은
정책에 따라 수시로 바뀝니다. 본 계산기는 기본 시나리오만 커버합니다.

참고 세율 (소득세법 §55, §104, 2024 기준 단순화)
- 보유기간 1년 미만: 70%
- 1~2년: 60%
- 2년 이상: 종합소득 누진세율(6~45%)
- 지방소득세: 산출세액의 10%
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from app.services.tax._brackets import apply_brackets

# 종합소득세 누진세율 (과세표준 원화 기준)
_INCOME_TAX_BRACKETS: list[tuple[Decimal | None, Decimal]] = [
    (Decimal("14000000"), Decimal("0.06")),
    (Decimal("50000000"), Decimal("0.15")),
    (Decimal("88000000"), Decimal("0.24")),
    (Decimal("150000000"), Decimal("0.35")),
    (Decimal("300000000"), Decimal("0.38")),
    (Decimal("500000000"), Decimal("0.40")),
    (Decimal("1000000000"), Decimal("0.42")),
    (None, Decimal("0.45")),
]

# 1세대1주택 장기보유특별공제 (최대 80%, 보유기간 40% + 거주기간 40%)
# - 보유기간: 3년 이상부터 매년 4%p (최대 10년 40%)
# - 거주기간: 2년 이상부터 매년 4%p (최대 10년 40%, 2년 거주는 8%)
# 다주택(중과 제외)은 최대 30%, 3년 이상부터 매년 2%p.


def _ltc_rate(hold_years: int, live_years: int, is_single_home: bool) -> Decimal:
    if hold_years < 3:
        return Decimal("0")
    if is_single_home:
        hold_pct = min(Decimal("0.04") * Decimal(hold_years), Decimal("0.40"))
        if live_years < 2:
            live_pct = Decimal("0")
        else:
            live_pct = min(Decimal("0.04") * Decimal(live_years), Decimal("0.40"))
        return min(hold_pct + live_pct, Decimal("0.80"))
    # 다주택 (일반공제): 3년 6% + 매년 2%p, 상한 30%
    base = Decimal("0.06")
    extra = Decimal("0.02") * Decimal(max(hold_years - 3, 0))
    return min(base + extra, Decimal("0.30"))


@dataclass(slots=True)
class CapitalGainsInput:
    sale_price: Decimal
    acquisition_price: Decimal
    expenses: Decimal = Decimal("0")           # 필요경비 (중개수수료·법무비 등)
    hold_years: int = 0
    live_years: int = 0
    is_single_home: bool = False
    is_heavy_multi: bool = False               # 다주택 중과대상 (+20%p or +30%p)
    heavy_surcharge_pp: int = 20               # 중과 가산 세율(pp)


@dataclass(slots=True)
class CapitalGainsResult:
    gain: Decimal              # 양도차익
    long_term_discount: Decimal
    taxable_base: Decimal
    applied_rate_label: str
    gross_tax: Decimal
    local_income_tax: Decimal
    total: Decimal

    def as_dict(self) -> dict:
        return {k: str(v) for k, v in self.__dict__.items()}


_BASIC_DEDUCTION = Decimal("2500000")  # 기본공제 250만원/인


def calc_capital_gains_tax(i: CapitalGainsInput) -> CapitalGainsResult:
    gain = i.sale_price - i.acquisition_price - i.expenses
    gain = max(gain, Decimal("0"))

    ltc_rate = _ltc_rate(i.hold_years, i.live_years, i.is_single_home)
    ltc = (gain * ltc_rate).quantize(Decimal("1"))
    after_ltc = max(gain - ltc, Decimal("0"))
    base = max(after_ltc - _BASIC_DEDUCTION, Decimal("0"))

    if i.hold_years < 1:
        rate = Decimal("0.70")
        label = "단기(1년 미만) 70%"
        gross = (base * rate).quantize(Decimal("1"))
    elif i.hold_years < 2:
        rate = Decimal("0.60")
        label = "단기(1~2년) 60%"
        gross = (base * rate).quantize(Decimal("1"))
    else:
        gross = apply_brackets(base, _INCOME_TAX_BRACKETS).quantize(Decimal("1"))
        label = "종합소득 누진세율(6~45%)"
        if i.is_heavy_multi:
            surcharge = (base * Decimal(i.heavy_surcharge_pp) / Decimal("100")).quantize(
                Decimal("1")
            )
            gross += surcharge
            label += f" + 중과가산 {i.heavy_surcharge_pp}pp"

    local = (gross * Decimal("0.10")).quantize(Decimal("1"))
    return CapitalGainsResult(
        gain=gain,
        long_term_discount=ltc,
        taxable_base=base,
        applied_rate_label=label,
        gross_tax=gross,
        local_income_tax=local,
        total=gross + local,
    )
