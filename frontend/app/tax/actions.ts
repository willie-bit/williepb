"use server";

import { apiFetch } from "@/lib/api";

export type PropertyTaxResponse = {
  tax_base: string;
  property_tax: string;
  urban_area_tax: string;
  local_education_tax: string;
  total: string;
};

export type ComprehensiveTaxResponse = {
  gross_price: string;
  deduction: string;
  tax_base: string;
  gross_tax: string;
  rural_special_tax: string;
  total: string;
  applied_rate_table: string;
};

export type CapitalGainsResponse = {
  gain: string;
  long_term_discount: string;
  taxable_base: string;
  applied_rate_label: string;
  gross_tax: string;
  local_income_tax: string;
  total: string;
};

export async function calcPropertyTax(payload: {
  published_price: string;
  city_area: boolean;
}): Promise<PropertyTaxResponse> {
  return apiFetch<PropertyTaxResponse>("/api/v1/tax/property", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function calcComprehensiveTax(payload: {
  published_prices: string[];
  is_single_household_single_home: boolean;
  is_multi_home_heavy: boolean;
}): Promise<ComprehensiveTaxResponse> {
  return apiFetch<ComprehensiveTaxResponse>("/api/v1/tax/comprehensive", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function calcCapitalGainsTax(payload: {
  sale_price: string;
  acquisition_price: string;
  expenses: string;
  hold_years: number;
  live_years: number;
  is_single_home: boolean;
  is_heavy_multi: boolean;
  heavy_surcharge_pp: number;
}): Promise<CapitalGainsResponse> {
  return apiFetch<CapitalGainsResponse>("/api/v1/tax/capital-gains", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
