from decimal import Decimal

from pydantic import BaseModel, Field


class PropertyTaxRequest(BaseModel):
    published_price: Decimal = Field(ge=0, description="공시가격 (원)")
    city_area: bool = True


class PropertyTaxResponse(BaseModel):
    tax_base: Decimal
    property_tax: Decimal
    urban_area_tax: Decimal
    local_education_tax: Decimal
    total: Decimal


class ComprehensiveTaxRequest(BaseModel):
    published_prices: list[Decimal] = Field(min_length=1)
    is_single_household_single_home: bool = True
    is_multi_home_heavy: bool = False


class ComprehensiveTaxResponse(BaseModel):
    gross_price: Decimal
    deduction: Decimal
    tax_base: Decimal
    gross_tax: Decimal
    rural_special_tax: Decimal
    total: Decimal
    applied_rate_table: str


class CapitalGainsRequest(BaseModel):
    sale_price: Decimal = Field(ge=0)
    acquisition_price: Decimal = Field(ge=0)
    expenses: Decimal = Decimal("0")
    hold_years: int = Field(ge=0, le=60)
    live_years: int = Field(ge=0, le=60)
    is_single_home: bool = False
    is_heavy_multi: bool = False
    heavy_surcharge_pp: int = Field(default=20, ge=0, le=40)


class CapitalGainsResponse(BaseModel):
    gain: Decimal
    long_term_discount: Decimal
    taxable_base: Decimal
    applied_rate_label: str
    gross_tax: Decimal
    local_income_tax: Decimal
    total: Decimal
