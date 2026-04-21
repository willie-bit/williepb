export type AssetType =
  | "REAL_ESTATE"
  | "STOCK"
  | "ETF"
  | "FUND"
  | "PENSION"
  | "CASH"
  | "CRYPTO"
  | "GOLD_PHYSICAL"
  | "GOLD_FINANCIAL"
  | "VEHICLE"
  | "OTHER";

export type ValuationSource = "REALTIME" | "DAILY" | "MANUAL";

export type LiabilityType =
  | "MORTGAGE"
  | "CREDIT_LOAN"
  | "CARD_INSTALLMENT"
  | "CARD_BALANCE"
  | "PRIVATE_LOAN"
  | "OTHER";

export type RateType = "FIXED" | "FLOAT";

export type Role = "OWNER" | "CO_ADMIN" | "VIEWER";

export type AllocationSlice = {
  key: string;
  label: string;
  value: string;
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

export type NetWorthPoint = {
  date: string;
  total_assets: string;
  total_liabilities: string;
  net_worth: string;
};

export type NetWorthSeries = { points: NetWorthPoint[] };

export type Asset = {
  id: number;
  household_id: number;
  account_id: number | null;
  asset_type: AssetType;
  label: string;
  symbol: string | null;
  currency: string;
  quantity: string;
  cost_basis_avg: string | null;
  manual_value: string | null;
  valuation_source: ValuationSource;
  asset_metadata: Record<string, unknown> | null;
  created_at: string;
};

export type AssetCreate = {
  household_id: number;
  account_id?: number | null;
  asset_type: AssetType;
  label: string;
  symbol?: string | null;
  currency?: string;
  quantity?: string;
  cost_basis_avg?: string | null;
  manual_value?: string | null;
  valuation_source?: ValuationSource;
  asset_metadata?: Record<string, unknown> | null;
};

export type Liability = {
  id: number;
  household_id: number;
  owner_member_id: number;
  institution_code: string | null;
  liability_type: LiabilityType;
  label: string;
  principal: string;
  balance: string;
  interest_rate: string | null;
  rate_type: RateType;
  currency: string;
  start_date: string | null;
  maturity_date: string | null;
  created_at: string;
};

export type LiabilityCreate = {
  household_id: number;
  owner_member_id: number;
  institution_code?: string | null;
  liability_type: LiabilityType;
  label: string;
  principal: string;
  balance: string;
  interest_rate?: string | null;
  rate_type?: RateType;
  currency?: string;
  start_date?: string | null;
  maturity_date?: string | null;
};

export type Member = {
  id: number;
  household_id: number;
  name: string;
  email: string | null;
  role: Role;
  created_at: string;
};

export type CurrentUser = {
  id: number;
  email: string;
  created_at: string;
  member_id: number | null;
  household_id: number | null;
  household_name: string | null;
  display_name: string | null;
  role: Role | null;
};
