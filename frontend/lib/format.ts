const krwFormatter = new Intl.NumberFormat("ko-KR", {
  style: "currency",
  currency: "KRW",
  maximumFractionDigits: 0,
});

const pctFormatter = new Intl.NumberFormat("ko-KR", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

export function formatKRW(value: string | number): string {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "-";
  return krwFormatter.format(n);
}

export function formatSignedKRW(value: string | number): string {
  const n = typeof value === "string" ? Number(value) : value;
  if (Number.isNaN(n)) return "-";
  const sign = n > 0 ? "+" : "";
  return sign + krwFormatter.format(n);
}

export function formatPct(ratio: number): string {
  return pctFormatter.format(ratio);
}
