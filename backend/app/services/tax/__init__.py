from app.services.tax.capital_gains import (
    CapitalGainsInput,
    CapitalGainsResult,
    calc_capital_gains_tax,
)
from app.services.tax.property import (
    ComprehensiveTaxInput,
    ComprehensiveTaxResult,
    PropertyTaxInput,
    PropertyTaxResult,
    calc_comprehensive_real_estate_tax,
    calc_property_tax,
)

__all__ = [
    "PropertyTaxInput",
    "PropertyTaxResult",
    "calc_property_tax",
    "ComprehensiveTaxInput",
    "ComprehensiveTaxResult",
    "calc_comprehensive_real_estate_tax",
    "CapitalGainsInput",
    "CapitalGainsResult",
    "calc_capital_gains_tax",
]
