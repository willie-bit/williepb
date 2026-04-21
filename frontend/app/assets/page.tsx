import AppShell from "@/components/AppShell";
import { apiFetch } from "@/lib/api";
import { requireUser } from "@/lib/auth";
import { formatKRW } from "@/lib/format";
import type { Asset } from "@/lib/types";
import AssetsTable from "./AssetsTable";
import { AssetForm } from "./AssetForm";

const TYPE_LABEL: Record<string, string> = {
  REAL_ESTATE: "부동산",
  STOCK: "주식",
  ETF: "ETF",
  FUND: "펀드",
  PENSION: "연금",
  CASH: "현금",
  CRYPTO: "암호화폐",
  GOLD_PHYSICAL: "금(현물)",
  GOLD_FINANCIAL: "금(금융)",
  VEHICLE: "자동차",
  OTHER: "기타",
};

export default async function AssetsPage() {
  return (
    <AppShell>
      <Content />
    </AppShell>
  );
}

async function Content() {
  const me = await requireUser();
  const assets = await apiFetch<Asset[]>("/api/v1/assets");
  const householdId = me.household_id!;

  const byType = assets.reduce<Record<string, Asset[]>>((acc, a) => {
    (acc[a.asset_type] ||= []).push(a);
    return acc;
  }, {});

  return (
    <>
      <div className="toolbar">
        <h1 style={{ margin: 0 }}>자산 관리</h1>
      </div>

      <section className="card" style={{ marginBottom: 20 }}>
        <h2>새 자산 등록</h2>
        <AssetForm householdId={householdId} typeLabels={TYPE_LABEL} />
      </section>

      <section className="card">
        <h2>등록된 자산 ({assets.length}건)</h2>
        {assets.length === 0 ? (
          <p className="muted" style={{ fontSize: 13 }}>
            위 폼으로 첫 자산을 등록해 보세요. 부동산은 공시가(또는 감정가)를
            <code> 수동가(manual_value) </code>에 넣어 주세요.
          </p>
        ) : (
          <AssetsTable assets={assets} typeLabels={TYPE_LABEL} />
        )}
      </section>

      <section className="card" style={{ marginTop: 20 }}>
        <h2>요약</h2>
        <table>
          <thead>
            <tr>
              <th>자산군</th>
              <th className="num">건수</th>
              <th className="num">합계(수동가+취득가 기준 단순 합)</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(byType).map(([t, list]) => {
              const sum = list.reduce(
                (acc, a) =>
                  acc +
                  (a.manual_value
                    ? Number(a.manual_value)
                    : Number(a.cost_basis_avg ?? 0) * Number(a.quantity)),
                0,
              );
              return (
                <tr key={t}>
                  <td>{TYPE_LABEL[t] ?? t}</td>
                  <td className="num">{list.length}</td>
                  <td className="num">{formatKRW(sum)}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </section>
    </>
  );
}
