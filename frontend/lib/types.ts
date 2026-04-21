export type AllocationSlice = {
  key: string;
  label: string;
  value: string; // Decimal serialized as string
  ratio: number;
};

export type MemberBreakdown = {
  member_id: number;
  member_name: string;
  assets: string;
  liabilities: string;
  net_worth: string;
};

export type MonthlyPnL = {
  year_month: string;
  realized: string;
  unrealized_change: string;
  cashflow_in: string;
  cashflow_out: string;
  net: string;
};

export type Dashboard = {
  household_id: number;
  as_of: string;
  total_assets: string;
  total_liabilities: string;
  net_worth: string;
  by_asset_type: AllocationSlice[];
  by_member: MemberBreakdown[];
  recent_monthly_pnl: MonthlyPnL[];
};
