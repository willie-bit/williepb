"use client";

import { useState, useTransition } from "react";
import { createAssetAction } from "@/lib/actions";

type Props = {
  householdId: number;
  typeLabels: Record<string, string>;
};

export function AssetForm({ householdId, typeLabels }: Props) {
  const [error, setError] = useState<string | null>(null);
  const [assetType, setAssetType] = useState<string>("STOCK");
  const [pending, start] = useTransition();

  const onSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const data = new FormData(form);
    start(async () => {
      const res = await createAssetAction(data);
      if (res?.error) setError(res.error);
      else {
        setError(null);
        form.reset();
        setAssetType("STOCK");
      }
    });
  };

  const showSymbol = ["STOCK", "ETF", "FUND", "CRYPTO", "GOLD_FINANCIAL", "GOLD_PHYSICAL"].includes(
    assetType,
  );
  const showManual = ["REAL_ESTATE", "VEHICLE", "OTHER", "CASH", "PENSION"].includes(assetType);
  const showQty = showSymbol;

  return (
    <form onSubmit={onSubmit}>
      <input type="hidden" name="household_id" value={householdId} />
      <div className="form-row inline">
        <div>
          <label htmlFor="asset_type">자산군</label>
          <select
            id="asset_type"
            name="asset_type"
            value={assetType}
            onChange={(e) => setAssetType(e.target.value)}
          >
            {Object.entries(typeLabels).map(([k, v]) => (
              <option key={k} value={k}>
                {v}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label htmlFor="label">이름</label>
          <input id="label" name="label" required maxLength={160} />
        </div>
      </div>

      {showSymbol ? (
        <div className="form-row inline">
          <div>
            <label htmlFor="symbol">심볼/종목코드</label>
            <input
              id="symbol"
              name="symbol"
              placeholder="예: 005930, KRW-BTC, 069500"
            />
          </div>
          <div>
            <label htmlFor="currency">통화</label>
            <select id="currency" name="currency" defaultValue="KRW">
              <option value="KRW">KRW</option>
              <option value="USD">USD</option>
              <option value="JPY">JPY</option>
              <option value="EUR">EUR</option>
            </select>
          </div>
        </div>
      ) : null}

      {showQty ? (
        <div className="form-row inline">
          <div>
            <label htmlFor="quantity">수량</label>
            <input
              id="quantity"
              name="quantity"
              type="number"
              step="0.00000001"
              defaultValue="0"
            />
          </div>
          <div>
            <label htmlFor="cost_basis_avg">평균매수가</label>
            <input id="cost_basis_avg" name="cost_basis_avg" type="number" step="0.01" />
          </div>
        </div>
      ) : null}

      {showManual ? (
        <div className="form-row">
          <label htmlFor="manual_value">수동 평가액 (KRW)</label>
          <input id="manual_value" name="manual_value" type="number" step="1" required />
        </div>
      ) : null}

      <input type="hidden" name="valuation_source" value={showSymbol ? "DAILY" : "MANUAL"} />

      {error ? <div className="error">{error}</div> : null}
      <button type="submit" disabled={pending} style={{ marginTop: 4 }}>
        {pending ? "등록 중…" : "자산 추가"}
      </button>
    </form>
  );
}
