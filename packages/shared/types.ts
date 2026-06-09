export type PlatformMode = "centralized" | "decentralized" | "hybrid";

export interface TickerPair {
  symbol: string;
  price: number;
  change: number;
}

export interface OrderBookEntry {
  price: number;
  amount: number;
}

export interface HybridBalances {
  tess_id: string;
  cefi_balance: number;
  defi_balance: number;
  hyb_balance: number;
  dag_finality_ms: number;
  settlement_secure: boolean;
}

export interface LivingRelic {
  token_id: string;
  name: string;
  description: string;
  image_url: string;
  type: string;
  status: string;
  soul_reserve: number;
}

export interface DaoProposal {
  id: number;
  title: string;
  description: string;
  status: string;
  votes_for: number;
  votes_against: number;
  ends_at: string;
}

export interface DefiPool {
  pair: string;
  tvl: number;
  apy: number;
  volume_24h: number;
}

export interface TessAgent {
  id: number;
  name: string;
  type: string;
  description: string;
  status: string;
  budget: number;
  stake: number;
}
