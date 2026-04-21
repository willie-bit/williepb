"use client";

import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { NetWorthPoint } from "@/lib/types";
import { formatKRW } from "@/lib/format";

export default function NetWorthTimeline({ points }: { points: NetWorthPoint[] }) {
  const data = points.map((p) => ({
    date: p.date,
    net_worth: Number(p.net_worth),
    total_assets: Number(p.total_assets),
  }));
  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 16, left: 0, bottom: 0 }}>
          <defs>
            <linearGradient id="nw" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#6ea8ff" stopOpacity={0.4} />
              <stop offset="100%" stopColor="#6ea8ff" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#242832" />
          <XAxis dataKey="date" stroke="#8b93a7" fontSize={11} tickMargin={4} />
          <YAxis
            stroke="#8b93a7"
            fontSize={11}
            tickFormatter={(v) => `${(v / 100000000).toFixed(1)}억`}
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
          <Area
            type="monotone"
            dataKey="net_worth"
            name="순자산"
            stroke="#6ea8ff"
            fill="url(#nw)"
            strokeWidth={2}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
