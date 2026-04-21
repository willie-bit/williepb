"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { MonthlyPnL } from "@/lib/types";
import { formatKRW } from "@/lib/format";

export default function MonthlyPnLBars({ rows }: { rows: MonthlyPnL[] }) {
  const data = rows.map((r) => ({
    month: r.year_month.slice(5),
    net: Number(r.net),
  }));
  return (
    <div style={{ height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#242832" />
          <XAxis dataKey="month" stroke="#8b93a7" fontSize={11} />
          <YAxis
            stroke="#8b93a7"
            fontSize={11}
            tickFormatter={(v) => `${(v / 10000).toFixed(0)}만`}
            width={60}
          />
          <Tooltip
            contentStyle={{
              background: "#1d212a",
              border: "1px solid #242832",
              borderRadius: 6,
              color: "#e6e8ec",
            }}
            labelStyle={{ color: "#8b93a7" }}
            formatter={(value) => formatKRW(Number(value ?? 0))}
          />
          <Bar dataKey="net" name="월 손익">
            {data.map((d, i) => (
              <Cell key={i} fill={d.net >= 0 ? "#4fd18b" : "#ff6b6b"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
