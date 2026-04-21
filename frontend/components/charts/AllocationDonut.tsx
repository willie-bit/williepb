"use client";

import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from "recharts";
import type { AllocationSlice } from "@/lib/types";
import { formatKRW } from "@/lib/format";

const PALETTE = [
  "#6ea8ff",
  "#4fd18b",
  "#d4af37",
  "#ff9f43",
  "#b388ff",
  "#ff6b9b",
  "#58c7f3",
  "#a0a0a0",
  "#8b93a7",
  "#e74c3c",
  "#f1c40f",
];

export default function AllocationDonut({ data }: { data: AllocationSlice[] }) {
  const chartData = data.map((d) => ({
    name: d.label,
    value: Number(d.value),
    ratio: d.ratio,
  }));
  return (
    <div style={{ height: 280 }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Pie
            data={chartData}
            innerRadius={60}
            outerRadius={95}
            dataKey="value"
            nameKey="name"
            stroke="none"
          >
            {chartData.map((_, i) => (
              <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
            ))}
          </Pie>
          <Tooltip
            contentStyle={{
              background: "#1d212a",
              border: "1px solid #242832",
              borderRadius: 6,
              color: "#e6e8ec",
            }}
            formatter={(value, name, entry) => {
              const ratio =
                (entry as { payload?: { ratio?: number } })?.payload?.ratio ?? 0;
              return [
                `${formatKRW(Number(value ?? 0))} (${(ratio * 100).toFixed(1)}%)`,
                String(name ?? ""),
              ];
            }}
          />
          <Legend
            wrapperStyle={{ fontSize: 12, color: "#8b93a7" }}
            formatter={(value: string) => <span style={{ color: "#e6e8ec" }}>{value}</span>}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
}
