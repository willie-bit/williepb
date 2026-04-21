from dataclasses import asdict

from fastapi import APIRouter, Depends

from app.api.deps import get_auth_context
from app.schemas.tax import (
    CapitalGainsRequest,
    CapitalGainsResponse,
    ComprehensiveTaxRequest,
    ComprehensiveTaxResponse,
    PropertyTaxRequest,
    PropertyTaxResponse,
)
from app.services.tax import (
    CapitalGainsInput,
    ComprehensiveTaxInput,
    PropertyTaxInput,
    calc_capital_gains_tax,
    calc_comprehensive_real_estate_tax,
    calc_property_tax,
)

router = APIRouter(prefix="/tax", tags=["tax"], dependencies=[Depends(get_auth_context)])


@router.post("/property", response_model=PropertyTaxResponse)
def property_tax(body: PropertyTaxRequest) -> PropertyTaxResponse:
    r = calc_property_tax(
        PropertyTaxInput(published_price=body.published_price, city_area=body.city_area)
    )
    return PropertyTaxResponse(**asdict(r))


@router.post("/comprehensive", response_model=ComprehensiveTaxResponse)
def comprehensive_tax(body: ComprehensiveTaxRequest) -> ComprehensiveTaxResponse:
    r = calc_comprehensive_real_estate_tax(
        ComprehensiveTaxInput(
            published_prices=body.published_prices,
            is_single_household_single_home=body.is_single_household_single_home,
            is_multi_home_heavy=body.is_multi_home_heavy,
        )
    )
    return ComprehensiveTaxResponse(**asdict(r))


@router.post("/capital-gains", response_model=CapitalGainsResponse)
def capital_gains_tax(body: CapitalGainsRequest) -> CapitalGainsResponse:
    r = calc_capital_gains_tax(
        CapitalGainsInput(
            sale_price=body.sale_price,
            acquisition_price=body.acquisition_price,
            expenses=body.expenses,
            hold_years=body.hold_years,
            live_years=body.live_years,
            is_single_home=body.is_single_home,
            is_heavy_multi=body.is_heavy_multi,
            heavy_surcharge_pp=body.heavy_surcharge_pp,
        )
    )
    return CapitalGainsResponse(**asdict(r))
