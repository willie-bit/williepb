"use server";

import { revalidatePath } from "next/cache";
import { apiFetch } from "./api";
import type {
  Asset,
  AssetCreate,
  AssetType,
  Liability,
  LiabilityCreate,
  LiabilityType,
  ValuationSource,
} from "./types";

export async function createAssetAction(
  formData: FormData,
): Promise<{ error?: string }> {
  const household_id = Number(formData.get("household_id"));
  const asset_type = String(formData.get("asset_type")) as AssetType;
  const valuation_source = String(
    formData.get("valuation_source") ?? "MANUAL",
  ) as ValuationSource;
  const body: AssetCreate = {
    household_id,
    asset_type,
    label: String(formData.get("label") ?? ""),
    symbol: emptyToNull(formData.get("symbol")),
    currency: String(formData.get("currency") ?? "KRW"),
    quantity: String(formData.get("quantity") ?? "0"),
    cost_basis_avg: emptyToNull(formData.get("cost_basis_avg")),
    manual_value: emptyToNull(formData.get("manual_value")),
    valuation_source,
  };
  try {
    await apiFetch<Asset>("/api/v1/assets", {
      method: "POST",
      body: JSON.stringify(body),
    });
  } catch (err) {
    return { error: err instanceof Error ? err.message : "자산 등록 실패" };
  }
  revalidatePath("/assets");
  revalidatePath("/dashboard");
  return {};
}

export async function deleteAssetAction(id: number): Promise<void> {
  await apiFetch<null>(`/api/v1/assets/${id}`, { method: "DELETE" });
  revalidatePath("/assets");
  revalidatePath("/dashboard");
}

export async function createLiabilityAction(
  formData: FormData,
): Promise<{ error?: string }> {
  const household_id = Number(formData.get("household_id"));
  const owner_member_id = Number(formData.get("owner_member_id"));
  const body: LiabilityCreate = {
    household_id,
    owner_member_id,
    institution_code: emptyToNull(formData.get("institution_code")),
    liability_type: String(formData.get("liability_type")) as LiabilityType,
    label: String(formData.get("label") ?? ""),
    principal: String(formData.get("principal") ?? "0"),
    balance: String(formData.get("balance") ?? "0"),
    interest_rate: emptyToNull(formData.get("interest_rate")),
    rate_type:
      (formData.get("rate_type") as "FIXED" | "FLOAT" | null) ?? "FIXED",
    currency: "KRW",
    start_date: emptyToNull(formData.get("start_date")),
    maturity_date: emptyToNull(formData.get("maturity_date")),
  };
  try {
    await apiFetch<Liability>("/api/v1/liabilities", {
      method: "POST",
      body: JSON.stringify(body),
    });
  } catch (err) {
    return { error: err instanceof Error ? err.message : "부채 등록 실패" };
  }
  revalidatePath("/liabilities");
  revalidatePath("/dashboard");
  return {};
}

export async function deleteLiabilityAction(id: number): Promise<void> {
  await apiFetch<null>(`/api/v1/liabilities/${id}`, { method: "DELETE" });
  revalidatePath("/liabilities");
  revalidatePath("/dashboard");
}

function emptyToNull(raw: FormDataEntryValue | null): string | null {
  if (raw === null) return null;
  const s = String(raw).trim();
  return s.length === 0 ? null : s;
}
