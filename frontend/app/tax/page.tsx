import AppShell from "@/components/AppShell";
import TaxSimulators from "./TaxSimulators";

export default async function TaxPage() {
  return (
    <AppShell>
      <h1>세무 시뮬레이션</h1>
      <p className="muted" style={{ marginTop: -12, marginBottom: 20, fontSize: 13 }}>
        본 계산기는 간이 시뮬레이션입니다. 실제 납부 금액은 정책·개별 공제 조건에 따라
        달라질 수 있으며, 중요한 의사결정 전에는 세무 전문가의 검토가 필요합니다.
      </p>
      <TaxSimulators />
    </AppShell>
  );
}
