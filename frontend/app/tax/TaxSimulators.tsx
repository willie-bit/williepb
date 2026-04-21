"use client";

import { useState, useTransition } from "react";
import { formatKRW } from "@/lib/format";
import {
  calcCapitalGainsTax,
  calcComprehensiveTax,
  calcPropertyTax,
  type CapitalGainsResponse,
  type ComprehensiveTaxResponse,
  type PropertyTaxResponse,
} from "./actions";

export default function TaxSimulators() {
  return (
    <div className="grid grid-2" style={{ gap: 16 }}>
      <PropertyCard />
      <ComprehensiveCard />
      <div style={{ gridColumn: "1 / -1" }}>
        <CapitalGainsCard />
      </div>
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div
      style={{
        display: "flex",
        justifyContent: "space-between",
        padding: "6px 0",
        borderBottom: "1px solid var(--border)",
      }}
    >
      <span className="muted" style={{ fontSize: 12 }}>
        {label}
      </span>
      <span style={{ fontVariantNumeric: "tabular-nums" }}>{value}</span>
    </div>
  );
}

function PropertyCard() {
  const [price, setPrice] = useState("1000000000");
  const [cityArea, setCityArea] = useState(true);
  const [result, setResult] = useState<PropertyTaxResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    start(async () => {
      try {
        setResult(await calcPropertyTax({ published_price: price, city_area: cityArea }));
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "계산 실패");
      }
    });
  };

  return (
    <section className="card">
      <h2>재산세 (주택)</h2>
      <form onSubmit={submit}>
        <div className="form-row">
          <label>공시가격 (원)</label>
          <input
            type="number"
            step="1"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
            required
          />
        </div>
        <div className="form-row">
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={cityArea}
              onChange={(e) => setCityArea(e.target.checked)}
              style={{ width: "auto" }}
            />
            도시지역분 부과
          </label>
        </div>
        <button type="submit" disabled={pending}>
          {pending ? "계산 중…" : "재산세 계산"}
        </button>
        {error ? <div className="error">{error}</div> : null}
      </form>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <Row label="과세표준" value={formatKRW(result.tax_base)} />
          <Row label="재산세 본세" value={formatKRW(result.property_tax)} />
          <Row label="도시지역분" value={formatKRW(result.urban_area_tax)} />
          <Row label="지방교육세" value={formatKRW(result.local_education_tax)} />
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "10px 0 0",
              fontWeight: 600,
            }}
          >
            <span>합계</span>
            <span className="positive">{formatKRW(result.total)}</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function ComprehensiveCard() {
  const [priceList, setPriceList] = useState("1500000000");
  const [single, setSingle] = useState(true);
  const [heavy, setHeavy] = useState(false);
  const [result, setResult] = useState<ComprehensiveTaxResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    const prices = priceList
      .split(/[,\n]/)
      .map((s) => s.trim())
      .filter(Boolean);
    start(async () => {
      try {
        setResult(
          await calcComprehensiveTax({
            published_prices: prices,
            is_single_household_single_home: single,
            is_multi_home_heavy: heavy,
          }),
        );
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "계산 실패");
      }
    });
  };

  return (
    <section className="card">
      <h2>종합부동산세 (가구 합산)</h2>
      <form onSubmit={submit}>
        <div className="form-row">
          <label>주택별 공시가격 (쉼표 또는 줄바꿈 구분)</label>
          <textarea
            rows={3}
            value={priceList}
            onChange={(e) => setPriceList(e.target.value)}
            placeholder="예: 1500000000, 800000000"
          />
        </div>
        <div className="form-row">
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={single}
              onChange={(e) => setSingle(e.target.checked)}
              style={{ width: "auto" }}
            />
            1세대 1주택 공제 (12억)
          </label>
        </div>
        <div className="form-row">
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={heavy}
              onChange={(e) => setHeavy(e.target.checked)}
              style={{ width: "auto" }}
            />
            중과 대상 (3주택↑ 또는 조정대상지역 2주택)
          </label>
        </div>
        <button type="submit" disabled={pending}>
          {pending ? "계산 중…" : "종부세 계산"}
        </button>
        {error ? <div className="error">{error}</div> : null}
      </form>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <Row label="합산 공시가격" value={formatKRW(result.gross_price)} />
          <Row label="공제액" value={formatKRW(result.deduction)} />
          <Row label="과세표준" value={formatKRW(result.tax_base)} />
          <Row label={`산출세액 (${result.applied_rate_table})`} value={formatKRW(result.gross_tax)} />
          <Row label="농어촌특별세" value={formatKRW(result.rural_special_tax)} />
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "10px 0 0",
              fontWeight: 600,
            }}
          >
            <span>합계</span>
            <span className="positive">{formatKRW(result.total)}</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}

function CapitalGainsCard() {
  const [sale, setSale] = useState("800000000");
  const [acq, setAcq] = useState("500000000");
  const [exp, setExp] = useState("15000000");
  const [hold, setHold] = useState(10);
  const [live, setLive] = useState(5);
  const [single, setSingle] = useState(true);
  const [heavy, setHeavy] = useState(false);
  const [surcharge, setSurcharge] = useState(20);
  const [result, setResult] = useState<CapitalGainsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, start] = useTransition();

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    start(async () => {
      try {
        setResult(
          await calcCapitalGainsTax({
            sale_price: sale,
            acquisition_price: acq,
            expenses: exp,
            hold_years: hold,
            live_years: live,
            is_single_home: single,
            is_heavy_multi: heavy,
            heavy_surcharge_pp: surcharge,
          }),
        );
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "계산 실패");
      }
    });
  };

  return (
    <section className="card">
      <h2>양도소득세 (주택)</h2>
      <form onSubmit={submit}>
        <div className="form-row inline">
          <div>
            <label>양도가 (KRW)</label>
            <input type="number" value={sale} onChange={(e) => setSale(e.target.value)} required />
          </div>
          <div>
            <label>취득가 (KRW)</label>
            <input type="number" value={acq} onChange={(e) => setAcq(e.target.value)} required />
          </div>
        </div>
        <div className="form-row inline">
          <div>
            <label>필요경비 (중개·법무비 등)</label>
            <input type="number" value={exp} onChange={(e) => setExp(e.target.value)} />
          </div>
          <div>
            <label>보유기간 (년)</label>
            <input
              type="number"
              value={hold}
              min={0}
              max={60}
              onChange={(e) => setHold(Number(e.target.value))}
            />
          </div>
        </div>
        <div className="form-row inline">
          <div>
            <label>거주기간 (년, 1세대1주택 공제에 영향)</label>
            <input
              type="number"
              value={live}
              min={0}
              max={60}
              onChange={(e) => setLive(Number(e.target.value))}
            />
          </div>
          <div>
            <label>중과 가산 (pp)</label>
            <input
              type="number"
              value={surcharge}
              min={0}
              max={40}
              onChange={(e) => setSurcharge(Number(e.target.value))}
              disabled={!heavy}
            />
          </div>
        </div>
        <div className="form-row" style={{ display: "flex", gap: 20 }}>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={single}
              onChange={(e) => setSingle(e.target.checked)}
              style={{ width: "auto" }}
            />
            1세대 1주택 (장특공제 최대 80%)
          </label>
          <label style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <input
              type="checkbox"
              checked={heavy}
              onChange={(e) => setHeavy(e.target.checked)}
              style={{ width: "auto" }}
            />
            다주택 중과
          </label>
        </div>
        <button type="submit" disabled={pending}>
          {pending ? "계산 중…" : "양도세 계산"}
        </button>
        {error ? <div className="error">{error}</div> : null}
      </form>
      {result ? (
        <div style={{ marginTop: 16 }}>
          <Row label="양도차익" value={formatKRW(result.gain)} />
          <Row label="장기보유특별공제" value={formatKRW(result.long_term_discount)} />
          <Row label="과세표준" value={formatKRW(result.taxable_base)} />
          <Row label={`산출세액 (${result.applied_rate_label})`} value={formatKRW(result.gross_tax)} />
          <Row label="지방소득세" value={formatKRW(result.local_income_tax)} />
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: "10px 0 0",
              fontWeight: 600,
            }}
          >
            <span>총 납부 예상</span>
            <span className="negative">{formatKRW(result.total)}</span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
