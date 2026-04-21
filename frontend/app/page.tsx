import type { Dashboard } from "@/lib/types";
import { formatKRW, formatPct, formatSignedKRW } from "@/lib/format";

async function fetchDashboard(householdId: number): Promise<Dashboard | null> {
  const base = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";
  try {
    const res = await fetch(`${base}/api/v1/dashboard/${householdId}`, {
      cache: "no-store",
    });
    if (!res.ok) return null;
    return (await res.json()) as Dashboard;
  } catch {
    return null;
  }
}

export default async function Page({
  searchParams,
}: {
  searchParams: { household?: string };
}) {
  const householdId = Number(searchParams.household ?? 1);
  const data = await fetchDashboard(householdId);

  return (
    <main>
      <h1>가족 자산 대시보드 {data ? `— ${data.household_id}번 가구` : ""}</h1>
      {!data ? (
        <div className="card">
          <h2>백엔드 연결 실패</h2>
          <p>
            <code>NEXT_PUBLIC_API_BASE</code> 에 백엔드 주소를 설정하고, 샘플 데이터가 필요하면
            <code> python -m scripts.seed </code> 로 시드 후 다시 시도해 주세요.
          </p>
          <p>
            URL 파라미터로 가구 ID 를 바꿀 수 있습니다: <code>/?household=1</code>
          </p>
        </div>
      ) : (
        <>
          <div className="grid" style={{ marginBottom: 24 }}>
            <Kpi label="총 자산" value={formatKRW(data.total_assets)} sub={`${data.as_of} 기준`} />
            <Kpi label="총 부채" value={formatKRW(data.total_liabilities)} />
            <Kpi
              label="순자산"
              value={formatKRW(data.net_worth)}
              sub={`구성원 ${data.by_member.length}명 합산`}
            />
          </div>

          <section className="card" style={{ marginBottom: 24 }}>
            <h2>자산군 구성</h2>
            <table>
              <thead>
                <tr>
                  <th>자산군</th>
                  <th className="num">평가액</th>
                  <th className="num">비중</th>
                  <th style={{ width: "30%" }}></th>
                </tr>
              </thead>
              <tbody>
                {data.by_asset_type.map((s) => (
                  <tr key={s.key}>
                    <td>{s.label}</td>
                    <td className="num">{formatKRW(s.value)}</td>
                    <td className="num">{formatPct(s.ratio)}</td>
                    <td>
                      <div className="bar">
                        <span style={{ width: `${(s.ratio * 100).toFixed(2)}%` }} />
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="card" style={{ marginBottom: 24 }}>
            <h2>구성원별 분해</h2>
            <table>
              <thead>
                <tr>
                  <th>구성원</th>
                  <th className="num">자산</th>
                  <th className="num">부채</th>
                  <th className="num">순자산</th>
                </tr>
              </thead>
              <tbody>
                {data.by_member.map((m) => (
                  <tr key={m.member_id}>
                    <td>{m.member_name}</td>
                    <td className="num">{formatKRW(m.assets)}</td>
                    <td className="num">{formatKRW(m.liabilities)}</td>
                    <td
                      className={`num ${Number(m.net_worth) < 0 ? "negative" : "positive"}`}
                    >
                      {formatSignedKRW(m.net_worth)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>

          <section className="card">
            <h2>월별 손익 (최근 6개월)</h2>
            <table>
              <thead>
                <tr>
                  <th>월</th>
                  <th className="num">실현</th>
                  <th className="num">평가손익</th>
                  <th className="num">수입</th>
                  <th className="num">지출</th>
                  <th className="num">합계</th>
                </tr>
              </thead>
              <tbody>
                {data.recent_monthly_pnl.map((r) => (
                  <tr key={r.year_month}>
                    <td>{r.year_month}</td>
                    <td className="num">{formatSignedKRW(r.realized)}</td>
                    <td className="num">{formatSignedKRW(r.unrealized_change)}</td>
                    <td className="num positive">{formatKRW(r.cashflow_in)}</td>
                    <td className="num negative">-{formatKRW(r.cashflow_out)}</td>
                    <td
                      className={`num ${Number(r.net) < 0 ? "negative" : "positive"}`}
                    >
                      {formatSignedKRW(r.net)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </section>
        </>
      )}
    </main>
  );
}

function Kpi({
  label,
  value,
  sub,
}: {
  label: string;
  value: string;
  sub?: string;
}) {
  return (
    <div className="card">
      <h2>{label}</h2>
      <div className="kpi-value">{value}</div>
      {sub ? <div className="kpi-sub">{sub}</div> : null}
    </div>
  );
}
