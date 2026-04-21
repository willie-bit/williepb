import AppShell from "@/components/AppShell";
import { apiFetch } from "@/lib/api";
import { requireUser } from "@/lib/auth";
import type { Liability, Member } from "@/lib/types";
import { LiabilityForm } from "./LiabilityForm";
import LiabilitiesTable from "./LiabilitiesTable";

const TYPE_LABEL: Record<string, string> = {
  MORTGAGE: "주택담보대출",
  CREDIT_LOAN: "신용대출",
  CARD_INSTALLMENT: "카드 할부",
  CARD_BALANCE: "카드 잔액",
  PRIVATE_LOAN: "사적 대출",
  OTHER: "기타",
};

export default async function LiabilitiesPage() {
  return (
    <AppShell>
      <Content />
    </AppShell>
  );
}

async function Content() {
  const me = await requireUser();
  const [liabs, members] = await Promise.all([
    apiFetch<Liability[]>("/api/v1/liabilities"),
    apiFetch<Member[]>("/api/v1/members"),
  ]);
  const householdId = me.household_id!;

  return (
    <>
      <h1>부채 관리</h1>

      <section className="card" style={{ marginBottom: 20 }}>
        <h2>새 부채 등록</h2>
        <LiabilityForm
          householdId={householdId}
          members={members}
          typeLabels={TYPE_LABEL}
        />
      </section>

      <section className="card">
        <h2>등록된 부채 ({liabs.length}건)</h2>
        {liabs.length === 0 ? (
          <p className="muted" style={{ fontSize: 13 }}>
            주담대·신용대출·카드 잔액 등을 입력해 두면 대시보드의 순자산이 바로 반영됩니다.
          </p>
        ) : (
          <LiabilitiesTable
            liabs={liabs}
            members={members}
            typeLabels={TYPE_LABEL}
          />
        )}
      </section>
    </>
  );
}
