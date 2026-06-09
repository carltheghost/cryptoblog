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

export interface MarketListing {
  id: number;
  title: string;
  description: string;
  price: number;
  currency: string;
  type?: string;
  image_url?: string;
}

export interface LivingRelicItem {
  token_id: string;
  name: string;
  description: string;
  image_url: string;
  type: string;
  status: string;
  soul_reserve: number;
}

export interface SupportTicket {
  id: number;
  subject: string;
  message: string;
  priority: string;
  status: string;
  response?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface RewardPool {
  name: string;
  amount: number;
  claimable?: number;
  token: string;
  description: string;
}

export interface CefiOrder {
  id: number;
  pair: string;
  side: string;
  type: string;
  price: number;
  amount: number;
  filled: number;
  status: string;
  created_at: string;
}

export interface DefiTransaction {
  id: number;
  type: string;
  from_token?: string;
  to_token?: string;
  amount: number;
  output_amount?: number;
  tx_hash?: string;
  status: string;
  created_at: string;
}
