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

export interface AgentDetail extends TessAgent {
  permissions?: Record<string, boolean>;
  performance?: { tasks_completed: number; accuracy: number; earnings: number };
}

export interface WalletConfig {
  tess_id: string;
  multisig: { enabled: boolean; threshold: number; keys_required: number };
  recovery: { configured: boolean; guardians: string[] };
  agent_plugins: { pricebot: boolean; rebalancer: boolean };
  batch_queue: { id: number; action: string; amount: number; token: string; target: string; status: string }[];
  privacy: { pseudonym_mode: boolean; zk_disclosure: boolean; tor_routing: boolean };
}

export interface CefiEarnData {
  staked_mganga: number;
  available_mganga: number;
  apy: number;
  rewards_accrued: number;
  products: { name: string; apy: number; min: number }[];
}
