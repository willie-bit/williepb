from decimal import Decimal

from app.services.tax import (
    CapitalGainsInput,
    ComprehensiveTaxInput,
    PropertyTaxInput,
    calc_capital_gains_tax,
    calc_comprehensive_real_estate_tax,
    calc_property_tax,
)


def test_property_tax_simple_apartment():
    # 공시가격 10억 → 과세표준 6억
    # 6천 × 0.1% + 9천 × 0.15% + 1.5억 × 0.25% + 3억 × 0.4%
    #   = 60,000 + 135,000 + 375,000 + 1,200,000 = 1,770,000
    # 도시지역분: 6억 × 0.14% = 840,000
    # 지방교육세: 재산세 × 20% = 354,000
    r = calc_property_tax(PropertyTaxInput(published_price=Decimal("1000000000")))
    assert r.tax_base == Decimal("600000000")
    assert r.property_tax == Decimal("1770000")
    assert r.urban_area_tax == Decimal("840000")
    assert r.local_education_tax == Decimal("354000")
    assert r.total == Decimal("2964000")


def test_property_tax_zero_published_price():
    r = calc_property_tax(PropertyTaxInput(published_price=Decimal("0")))
    assert r.total == Decimal("0")


def test_comprehensive_tax_single_home_under_deduction():
    # 공시가 10억, 1세대1주택 → 공제 12억 적용 → 과세표준 0
    r = calc_comprehensive_real_estate_tax(
        ComprehensiveTaxInput(
            published_prices=[Decimal("1000000000")],
            is_single_household_single_home=True,
        )
    )
    assert r.tax_base == Decimal("0")
    assert r.total == Decimal("0")


def test_comprehensive_tax_multi_home():
    # 합산 20억, 다주택 → 공제 9억, 과세표준 = (20억-9억) × 60% = 6.6억
    # 일반 세율 (1~2주택 비중과): 3억×0.5% + 3억×0.7% + 6천만×1%
    #   = 1,500,000 + 2,100,000 + 600,000 = 4,200,000
    r = calc_comprehensive_real_estate_tax(
        ComprehensiveTaxInput(
            published_prices=[Decimal("1200000000"), Decimal("800000000")],
            is_single_household_single_home=False,
            is_multi_home_heavy=False,
        )
    )
    assert r.gross_price == Decimal("2000000000")
    assert r.deduction == Decimal("900000000")
    assert r.tax_base == Decimal("660000000")
    assert r.gross_tax == Decimal("4200000")
    assert r.rural_special_tax == Decimal("840000")


def test_capital_gains_long_term_single_home_heavy_discount():
    # 1세대1주택, 12년 보유, 10년 거주 → LTC 80%
    # 5억 양도 - 3억 취득 - 1천 경비 = 1.99억 차익
    # LTC 80% 공제 후 3,980만원
    # 기본공제 250만 → 과세표준 3,730만원
    # 세율: 6% ~ 14m + 15% ~ 23.3m
    #   = 14,000,000 × 0.06 + (37,300,000 - 14,000,000) × 0.15
    #   = 840,000 + 3,495,000 = 4,335,000
    # 지방세 10% = 433,500
    r = calc_capital_gains_tax(
        CapitalGainsInput(
            sale_price=Decimal("500000000"),
            acquisition_price=Decimal("300000000"),
            expenses=Decimal("10000000"),
            hold_years=12,
            live_years=10,
            is_single_home=True,
        )
    )
    assert r.gain == Decimal("190000000")
    assert r.long_term_discount == Decimal("152000000")
    assert r.taxable_base == Decimal("35500000")
    # 14m × 6% + 21.5m × 15% = 840,000 + 3,225,000 = 4,065,000
    assert r.gross_tax == Decimal("4065000")
    assert r.local_income_tax == Decimal("406500")
    assert r.total == Decimal("4471500")


def test_capital_gains_short_term_70pct():
    r = calc_capital_gains_tax(
        CapitalGainsInput(
            sale_price=Decimal("200000000"),
            acquisition_price=Decimal("150000000"),
            hold_years=0,
        )
    )
    # gain 5천만, LTC 0, 기본공제 250만 → 과세표준 4,750만 × 70%
    assert r.gain == Decimal("50000000")
    assert r.long_term_discount == Decimal("0")
    assert r.taxable_base == Decimal("47500000")
    assert r.applied_rate_label.startswith("단기(1년 미만)")
    assert r.gross_tax == Decimal("33250000")
    assert r.total == Decimal("33250000") + Decimal("3325000")


def test_capital_gains_negative_gain_zero_tax():
    r = calc_capital_gains_tax(
        CapitalGainsInput(
            sale_price=Decimal("300000000"),
            acquisition_price=Decimal("500000000"),
            hold_years=5,
        )
    )
    assert r.gain == Decimal("0")
    assert r.total == Decimal("0")
