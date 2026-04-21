"""재산세 + 종합부동산세 계산기 (주택 기준, MVP 단순화 버전).

⚠️ 본 계산기는 시뮬레이션 목적이며, 공정시장가액비율·공제·세율 등은 연도별로
정책에 따라 변경됩니다. 세무사 검토가 필요한 경우 참고용으로만 사용하세요.

참고: 지방세법 제111조(재산세), 종합부동산세법 제8조·제9조 (2024 기준 단순화).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from app.services.tax._brackets import apply_brackets

# 주택분 재산세 (지방세법 §111, 공정시장가액비율 60%)
PROPERTY_FAIR_RATIO = Decimal("0.60")

# 과세표준 → 재산세 (주택분)
_PROPERTY_BRACKETS: list[tuple[Decimal | None, Decimal]] = [
    (Decimal("60000000"), Decimal("0.001")),       # 6천만원 이하 0.1%
    (Decimal("150000000"), Decimal("0.0015")),     # 6천만~1.5억 0.15%
    (Decimal("300000000"), Decimal("0.0025")),     # 1.5억~3억 0.25%
    (None, Decimal("0.004")),                       # 3억 초과 0.4%
]

# 종부세 공제액 (주택분)
COMPREHENSIVE_DEDUCTION_SINGLE = Decimal("1200000000")   # 1세대1주택 12억
COMPREHENSIVE_DEDUCTION_MULTI = Decimal("900000000")     # 다주택 9억
COMPREHENSIVE_FAIR_RATIO = Decimal("0.60")

# 다주택(3주택 이상 or 조정대상지역 2주택) 종부세율 (누진)
_COMP_BRACKETS_MULTI: list[tuple[Decimal | None, Decimal]] = [
    (Decimal("300000000"), Decimal("0.005")),   # 3억 이하 0.5%
    (Decimal("600000000"), Decimal("0.007")),   # 3~6억 0.7%
    (Decimal("1200000000"), Decimal("0.01")),   # 6~12억 1.0%
    (Decimal("2500000000"), Decimal("0.02")),   # 12~25억 2.0%
    (Decimal("5000000000"), Decimal("0.03")),   # 25~50억 3.0%
    (Decimal("9400000000"), Decimal("0.04")),   # 50~94억 4.0%
    (None, Decimal("0.05")),                     # 94억 초과 5.0%
]

# 일반(1~2주택 비조정) 종부세율
_COMP_BRACKETS_SINGLE: list[tuple[Decimal | None, Decimal]] = [
    (Decimal("300000000"), Decimal("0.005")),
    (Decimal("600000000"), Decimal("0.007")),
    (Decimal("1200000000"), Decimal("0.01")),
    (Decimal("2500000000"), Decimal("0.013")),
    (Decimal("5000000000"), Decimal("0.015")),
    (Decimal("9400000000"), Decimal("0.02")),
    (None, Decimal("0.027")),
]


@dataclass(slots=True)
class PropertyTaxInput:
    published_price: Decimal  # 공시가격
    city_area: bool = True    # 도시지역 여부 (도시지역분 부과)


@dataclass(slots=True)
class PropertyTaxResult:
    tax_base: Decimal
    property_tax: Decimal        # 재산세 본세
    urban_area_tax: Decimal      # 도시지역분 (과세표준 × 0.14%)
    local_education_tax: Decimal # 지방교육세 (재산세 × 20%)
    total: Decimal

    def as_dict(self) -> dict:
        return {k: str(v) for k, v in self.__dict__.items()}


def calc_property_tax(i: PropertyTaxInput) -> PropertyTaxResult:
    base = (i.published_price * PROPERTY_FAIR_RATIO).quantize(Decimal("1"))
    main = apply_brackets(base, _PROPERTY_BRACKETS).quantize(Decimal("1"))
    urban = (base * Decimal("0.0014")).quantize(Decimal("1")) if i.city_area else Decimal("0")
    local_edu = (main * Decimal("0.20")).quantize(Decimal("1"))
    total = main + urban + local_edu
    return PropertyTaxResult(
        tax_base=base,
        property_tax=main,
        urban_area_tax=urban,
        local_education_tax=local_edu,
        total=total,
    )


@dataclass(slots=True)
class ComprehensiveTaxInput:
    published_prices: list[Decimal] = field(default_factory=list)
    """가구 합산 주택 공시가격 리스트."""
    is_single_household_single_home: bool = True
    """1세대1주택 해당 여부."""
    is_multi_home_heavy: bool = False
    """3주택 이상 또는 조정대상지역 2주택 (중과 대상)."""


@dataclass(slots=True)
class ComprehensiveTaxResult:
    gross_price: Decimal
    deduction: Decimal
    tax_base: Decimal
    gross_tax: Decimal         # 산출세액
    rural_special_tax: Decimal # 농어촌특별세 (산출세액 × 20%)
    total: Decimal
    applied_rate_table: str

    def as_dict(self) -> dict:
        return {k: str(v) for k, v in self.__dict__.items()}


def calc_comprehensive_real_estate_tax(i: ComprehensiveTaxInput) -> ComprehensiveTaxResult:
    gross = sum(i.published_prices, start=Decimal("0"))
    if i.is_single_household_single_home and len(i.published_prices) == 1:
        deduction = COMPREHENSIVE_DEDUCTION_SINGLE
    else:
        deduction = COMPREHENSIVE_DEDUCTION_MULTI
    after_deduction = max(gross - deduction, Decimal("0"))
    base = (after_deduction * COMPREHENSIVE_FAIR_RATIO).quantize(Decimal("1"))

    if i.is_multi_home_heavy:
        table = _COMP_BRACKETS_MULTI
        label = "중과세율(3주택↑ or 조정 2주택)"
    else:
        table = _COMP_BRACKETS_SINGLE
        label = "일반세율(1~2주택)"

    gross_tax = apply_brackets(base, table).quantize(Decimal("1"))
    rural = (gross_tax * Decimal("0.20")).quantize(Decimal("1"))
    return ComprehensiveTaxResult(
        gross_price=gross,
        deduction=deduction,
        tax_base=base,
        gross_tax=gross_tax,
        rural_special_tax=rural,
        total=gross_tax + rural,
        applied_rate_table=label,
    )
