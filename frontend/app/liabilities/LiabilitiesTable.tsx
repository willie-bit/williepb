"use client";

import { useTransition } from "react";
import { deleteLiabilityAction } from "@/lib/actions";
import { formatKRW } from "@/lib/format";
import type { Liability, Member } from "@/lib/types";

export default function LiabilitiesTable({
  liabs,
  members,
  typeLabels,
}: {
  liabs: Liability[];
  members: Member[];
  typeLabels: Record<string, string>;
}) {
  const [pending, start] = useTransition();
  const memberMap = new Map(members.map((m) => [m.id, m.name]));

  const onDelete = (id: number) => {
    if (!confirm("이 부채를 삭제할까요?")) return;
    start(async () => {
      await deleteLiabilityAction(id);
    });
  };

  return (
    <table>
      <thead>
        <tr>
          <th>종류</th>
          <th>이름</th>
          <th>채무자</th>
          <th className="num">원금</th>
          <th className="num">잔액</th>
          <th className="num">금리</th>
          <th>금리유형</th>
          <th>만기</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {liabs.map((l) => (
          <tr key={l.id}>
            <td><span className="badge">{typeLabels[l.liability_type] ?? l.liability_type}</span></td>
            <td>{l.label}</td>
            <td>{memberMap.get(l.owner_member_id) ?? l.owner_member_id}</td>
            <td className="num">{formatKRW(l.principal)}</td>
            <td className="num negative">{formatKRW(l.balance)}</td>
            <td className="num">
              {l.interest_rate ? `${(Number(l.interest_rate) * 100).toFixed(2)}%` : "-"}
            </td>
            <td>{l.rate_type}</td>
            <td className="muted">{l.maturity_date ?? "-"}</td>
            <td style={{ textAlign: "right" }}>
              <button
                type="button"
                className="ghost"
                disabled={pending}
                onClick={() => onDelete(l.id)}
              >
                삭제
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
