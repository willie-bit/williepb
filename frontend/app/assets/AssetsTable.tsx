"use client";

import { useTransition } from "react";
import { deleteAssetAction } from "@/lib/actions";
import { formatKRW } from "@/lib/format";
import type { Asset } from "@/lib/types";

export default function AssetsTable({
  assets,
  typeLabels,
}: {
  assets: Asset[];
  typeLabels: Record<string, string>;
}) {
  const [pending, start] = useTransition();

  const onDelete = (id: number) => {
    if (!confirm("이 자산을 삭제할까요?")) return;
    start(async () => {
      await deleteAssetAction(id);
    });
  };

  return (
    <table>
      <thead>
        <tr>
          <th>자산군</th>
          <th>이름</th>
          <th>심볼</th>
          <th className="num">수량</th>
          <th className="num">매입평균</th>
          <th className="num">수동 평가액</th>
          <th>평가 방식</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {assets.map((a) => (
          <tr key={a.id}>
            <td>
              <span className="badge">{typeLabels[a.asset_type] ?? a.asset_type}</span>
            </td>
            <td>{a.label}</td>
            <td className="muted">{a.symbol ?? "-"}</td>
            <td className="num">{a.quantity}</td>
            <td className="num">
              {a.cost_basis_avg ? formatKRW(a.cost_basis_avg) : "-"}
            </td>
            <td className="num">{a.manual_value ? formatKRW(a.manual_value) : "-"}</td>
            <td>
              <span className="badge">{a.valuation_source}</span>
            </td>
            <td style={{ textAlign: "right" }}>
              <button
                type="button"
                className="ghost"
                disabled={pending}
                onClick={() => onDelete(a.id)}
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
