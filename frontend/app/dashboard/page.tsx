import AppShell from "@/components/AppShell";
import AllocationDonut from "@/components/charts/AllocationDonut";
import MonthlyPnLBars from "@/components/charts/MonthlyPnLBars";
import NetWorthTimeline from "@/components/charts/NetWorthTimeline";
import { apiFetch } from "@/lib/api";
import { formatKRW, formatPct, formatSignedKRW } from "@/lib/format";
import type { Dashboard, NetWorthSeries } from "@/lib/types";

async function loadData() {
  const [dashboard, timeseries] = await Promise.all([
    apiFetch<Dashboard>("/api/v1/dashboard"),
    apiFetch<NetWorthSeries>("/api/v1/timeseries/net-worth?days=90"),
  ]);
  return { dashboard, timeseries };
}

export default async function DashboardPage() {
  return (
    <AppShell>
      <Content />
    </AppShell>
  );
}

async function Content() {
  const { dashboard, timeseries } = await loadData();

  return (
    <>
      <h1>가족 자산 대시보드</h1>

      <div className="grid grid-3" style={{ marginBottom: 16 }}>
        <Kpi label="총 자산" value={formatKRW(dashboard.total_assets)} sub={`${dashboard.as_of} 기준`} />
        <Kpi label="총 부채" value={formatKRW(dashboard.total_liabilities)} />
        <Kpi
          label="순자산"
          value={formatKRW(dashboard.net_worth)}
          sub={`구성원 ${dashboard.by_member.length}명 합산`}
        />
      </div>

      <div className="grid grid-2" style={{ marginBottom: 16 }}>
        <section className="card">
          <h2>순자산 추이 (90일)</h2>
          {timeseries.points.length > 1 ? (
            <NetWorthTimeline points={timeseries.points} />
          ) : (
            <p className="muted" style={{ fontSize: 13 }}>
              스냅샷이 아직 쌓이지 않았습니다. 매일 배치가 돌면 그래프가 채워집니다.
            </p>
          )}
        </section>
        <section className="card">
          <h2>자산군 구성</h2>
          {dashboard.by_asset_type.length > 0 ? (
            <AllocationDonut data={dashboard.by_asset_type} />
          ) : (
            <p className="muted" style={{ fontSize: 13 }}>
              자산을 등록하면 비중이 표시됩니다.
            </p>
          )}
        </section>
      </div>

      <section className="card" style={{ marginBottom: 16 }}>
        <h2>자산군 상세</h2>
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
            {dashboard.by_asset_type.map((s) => (
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
            {dashboard.by_asset_type.length === 0 ? (
              <tr>
                <td colSpan={4} className="muted">
                  아직 자산이 없습니다.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </section>

      <div className="grid grid-2">
        <section className="card">
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
              {dashboard.by_member.map((m) => (
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
          <MonthlyPnLBars rows={dashboard.recent_monthly_pnl} />
          <table style={{ marginTop: 12 }}>
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
              {dashboard.recent_monthly_pnl.map((r) => (
                <tr key={r.year_month}>
                  <td>{r.year_month}</td>
                  <td className="num">{formatSignedKRW(r.realized)}</td>
                  <td className="num">{formatSignedKRW(r.unrealized_change)}</td>
                  <td className="num positive">{formatKRW(r.cashflow_in)}</td>
                  <td className="num negative">-{formatKRW(r.cashflow_out)}</td>
                  <td className={`num ${Number(r.net) < 0 ? "negative" : "positive"}`}>
                    {formatSignedKRW(r.net)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      </div>
    </>
  );
}

function Kpi({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div className="card">
      <h2>{label}</h2>
      <div className="kpi-value">{value}</div>
      {sub ? <div className="kpi-sub">{sub}</div> : null}
    </div>
  );
}
