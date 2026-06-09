import type {
  AgentDetail,
  CefiEarnData,
  CefiOrder,
  DefiTransaction,
  LivingRelicItem,
  MarketListing,
  RewardPool,
  SupportTicket,
  TessAgent,
  WalletConfig,
} from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T = Record<string, unknown>>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError(res.status, (data as { detail?: string }).detail || `API error: ${res.status}`);
  }
  if ((data as { error?: string }).error) {
    throw new ApiError(400, (data as { error: string }).error);
  }
  return data as T;
}

export const api = {
  health: () => fetchApi<{ status: string; platform: string }>("/api/health"),
  cefi: {
    account: () => fetchApi<{ tess_id: string; display_name: string; mganga_balance: number; usd_balance: number; kyc_status: string }>("/api/cefi/account"),
    orderbook: (pair: string) => fetchApi<{ pair: string; bids: { price: number; amount: number }[]; asks: { price: number; amount: number }[]; last_price: number }>(`/api/cefi/orderbook/${pair}`),
    ticker: () => fetchApi<{ pairs: { symbol: string; price: number; change: number }[] }>("/api/cefi/ticker"),
    chart: (pair: string) => fetchApi<{ candles: { open: number; high: number; low: number; close: number; time?: number }[] }>(`/api/cefi/chart/${pair}`),
    orders: () => fetchApi<CefiOrder[]>("/api/cefi/orders"),
    placeOrder: (data: object) => fetchApi("/api/cefi/orders", { method: "POST", body: JSON.stringify(data) }),
    cancelOrder: (id: number) => fetchApi(`/api/cefi/orders/${id}/cancel`, { method: "POST" }),
    fiatDeposit: (data: object) => fetchApi("/api/cefi/fiat/deposit", { method: "POST", body: JSON.stringify(data) }),
    compliance: () => fetchApi<{ kyc_status: string; aml_compliant: boolean; tier: string }>("/api/cefi/compliance/status"),
    fraudScore: () => fetchApi<{ score: number; recommendation: string; factors: { name: string; score: number }[] }>("/api/cefi/fraud-score"),
    custody: () => fetchApi<{ allocations: { asset: string; amount: number; storage: string }[] }>("/api/cefi/custody"),
    stats: () => fetchApi<{ volume_24h: number; open_interest: number; users_online: number; uptime: number }>("/api/cefi/stats"),
    earn: () => fetchApi<CefiEarnData>("/api/cefi/earn"),
    earnStake: (amount: number) => fetchApi("/api/cefi/earn/stake", { method: "POST", body: JSON.stringify({ amount }) }),
    earnClaim: () => fetchApi("/api/cefi/earn/claim", { method: "POST" }),
  },
  defi: {
    wallet: (tessId: string) => fetchApi<{ mwanjesa_balance: number; hyb_balance: number; staked_trd: number; staking_rewards: number; tokens: { symbol: string; balance: number; usd_value: number }[] }>(`/api/defi/wallet/${tessId}`),
    riskScore: () => fetchApi<{ score: number; recommendation: string; factors: { name: string; score: number }[] }>("/api/defi/risk-score"),
    swapQuote: (data: object) => fetchApi("/api/defi/swap/quote", { method: "POST", body: JSON.stringify(data) }),
    swapExecute: (data: object) => fetchApi("/api/defi/swap/execute", { method: "POST", body: JSON.stringify(data) }),
    staking: () => fetchApi<{ staked_amount: number; rewards: number; apy: number; available_balance: number }>("/api/defi/staking"),
    stake: (data: object) => fetchApi("/api/defi/stake", { method: "POST", body: JSON.stringify(data) }),
    unstake: (data: object) => fetchApi("/api/defi/unstake", { method: "POST", body: JSON.stringify(data) }),
    proposals: () => fetchApi<{ id: number; title: string; votes_for: number; votes_against: number }[]>("/api/defi/dao/proposals"),
    vote: (data: object) => fetchApi("/api/defi/dao/vote", { method: "POST", body: JSON.stringify(data) }),
    pools: () => fetchApi<{ pair: string; tvl: number; apy: number; volume_24h: number }[]>("/api/defi/pools"),
    relics: () => fetchApi<LivingRelicItem[]>("/api/defi/relics"),
    mintRelic: (data: object) => fetchApi("/api/defi/relics/mint", { method: "POST", body: JSON.stringify(data) }),
    validateRelic: (tokenId: string) => fetchApi(`/api/defi/relics/${tokenId}/validate`, { method: "POST" }),
    bridge: (data: object) => fetchApi("/api/defi/bridge", { method: "POST", body: JSON.stringify(data) }),
    crossChain: (data: object) => fetchApi("/api/defi/cross-chain", { method: "POST", body: JSON.stringify(data) }),
    transactions: () => fetchApi<DefiTransaction[]>("/api/defi/transactions"),
    stats: () => fetchApi<{ tvl: number; volume_24h: number; active_pools: number; avg_apy: number }>("/api/defi/stats"),
    childChain: () => fetchApi<{ name: string; tvl: number; block_time: number; validators: number }>("/api/defi/child-chain"),
  },
  identity: {
    get: (tessId: string) => fetchApi(`/api/identity/${tessId}`),
    hybridBalances: () => fetchApi<{ tess_id: string; cefi_balance: number; defi_balance: number; hyb_balance: number; dag_finality_ms: number }>("/api/identity/hybrid/balances"),
    updatePreferences: (tessId: string, data: object) =>
      fetchApi(`/api/identity/${tessId}/preferences`, { method: "PUT", body: JSON.stringify(data) }),
  },
  market: {
    listings: () => fetchApi<MarketListing[]>("/api/market/listings"),
    createListing: (data: object) => fetchApi("/api/market/listings", { method: "POST", body: JSON.stringify(data) }),
    purchase: (id: number) => fetchApi(`/api/market/purchase/${id}`, { method: "POST" }),
    barter: (data: object) => fetchApi("/api/market/barter", { method: "POST", body: JSON.stringify(data) }),
    barters: () => fetchApi<{ id: number; offer: { assets: string[] }; request: { assets: string[] }; status: string; created_at: string }[]>("/api/market/barter"),
    acceptBarter: (id: number) => fetchApi(`/api/market/barter/${id}/accept`, { method: "POST" }),
  },
  agents: {
    list: () => fetchApi<TessAgent[]>("/api/agents/"),
    get: (id: number) => fetchApi<AgentDetail>(`/api/agents/${id}`),
    create: (data: object) => fetchApi("/api/agents/", { method: "POST", body: JSON.stringify(data) }),
    execute: (id: number) => fetchApi<{ detail: string; earning: number; tasks_completed: number }>(`/api/agents/${id}/execute`, { method: "POST" }),
  },
  analytics: {
    overview: () => fetchApi<{
      volume_24h: number; cefi_volume_24h: number; defi_tx_24h: number; bridge_volume_24h: number;
      casino_bets_24h: number; casino_wagered_24h: number; orders_24h: number; pool_tvl: number;
      tesslink_edges: number; balances: Record<string, number>;
      chains: { name: string; status: string; load: number }[];
    }>("/api/analytics/overview"),
  },
  wallet: {
    config: () => fetchApi<WalletConfig>("/api/wallet/config"),
    setupMultisig: (data?: { threshold?: number; device_keys?: string[] }) =>
      fetchApi("/api/wallet/multisig", { method: "POST", body: JSON.stringify(data || {}) }),
    setupRecovery: (guardians?: string[]) =>
      fetchApi("/api/wallet/recovery", { method: "POST", body: JSON.stringify({ guardians: guardians || [] }) }),
    updatePlugins: (data: { pricebot?: boolean; rebalancer?: boolean }) =>
      fetchApi("/api/wallet/agent-plugins", { method: "PUT", body: JSON.stringify(data) }),
    addBatch: (data: { action: string; amount: number; token?: string; target?: string }) =>
      fetchApi("/api/wallet/batch", { method: "POST", body: JSON.stringify(data) }),
    executeBatch: () => fetchApi("/api/wallet/batch/execute", { method: "POST" }),
  },
  storage: {
    upload: async (file: File) => {
      const form = new FormData();
      form.append("file", file);
      const res = await fetch(`${API_URL}/api/storage/upload`, { method: "POST", body: form });
      if (!res.ok) throw new ApiError(res.status, "Upload failed");
      return res.json();
    },
    vaultStore: (field: string, value: string) =>
      fetchApi("/api/storage/vault/store", { method: "POST", body: JSON.stringify({ field, value }) }),
    tesslink: () => fetchApi<{ nodes: { id: string; type: string }[]; edges: { source: string; target: string; type: string }[] }>("/api/storage/tesslink/graph"),
    shadowProof: (tokenId: string) => fetchApi(`/api/storage/shadow-proof/${tokenId}`, { method: "POST" }),
  },
  rewards: {
    get: () => fetchApi<{ pools: RewardPool[]; total_claimable: number; cefi_earn_apy: number; defi_staking_apy: number }>("/api/rewards/"),
    claim: () => fetchApi("/api/rewards/claim", { method: "POST" }),
  },
  support: {
    createTicket: (data: object) => fetchApi<{ id: number; response?: string }>("/api/support/tickets", { method: "POST", body: JSON.stringify(data) }),
    tickets: () => fetchApi<SupportTicket[]>("/api/support/tickets"),
    getTicket: (id: number) => fetchApi<SupportTicket>(`/api/support/tickets/${id}`),
    updateTicket: (id: number, data: { status: string }) =>
      fetchApi(`/api/support/tickets/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  },
  casino: {
    games: () => fetchApi("/api/casino/games"),
    wallet: () => fetchApi<{
      mganga_chips: number; mwanjesa_chips: number; total_wagered: number; total_won: number;
      games_played: number; win_streak: number; server_seed_hash: string; net_profit: number;
    }>("/api/casino/wallet"),
    bet: (data: { game: string; amount: number; currency?: string; choice?: string; client_seed?: string }) =>
      fetchApi<{
        bet_id: number; won: boolean; payout: number; multiplier: number; profit: number;
        outcome: Record<string, unknown>;
        proof: { algorithm: string; server_seed_hash: string; client_seed: string; nonce: number; digest: string; game: string };
        chips_remaining: number; win_streak: number;
      }>("/api/casino/bet", { method: "POST", body: JSON.stringify(data) }),
    deposit: (amount: number, currency: string) =>
      fetchApi("/api/casino/deposit", { method: "POST", body: JSON.stringify({ amount, currency }) }),
    history: () => fetchApi<{ id: number; game: string; amount: number; payout: number; won: boolean; multiplier: number }[]>("/api/casino/history"),
    leaderboard: () => fetchApi<{ rank: number; player: string; total_won: number; games_played: number; win_streak: number }[]>("/api/casino/leaderboard"),
    liveFeed: () => fetchApi<{ player: string; game: string; won: boolean; multiplier: number; payout: number; amount: number }[]>("/api/casino/live-feed"),
    verifyProof: (betId: number) => fetchApi<{ valid: boolean }>("/api/casino/rfsam/verify", { method: "POST", body: JSON.stringify({ bet_id: betId }) }),
    rotateSeed: () => fetchApi("/api/casino/rfsam/rotate-seed", { method: "POST" }),
  },
  omniverse: {
    status: () => fetchApi<{
      dimension: number; overdrive: boolean; quantum_locked: boolean; paradox_count: number;
      hive_sync_percent: number; soul_resonance: number; impossibility_index: number; reality_stability: number;
    }>("/api/omniverse/status"),
    overdrive: () => fetchApi<{ overdrive: boolean; message: string }>("/api/omniverse/overdrive", { method: "POST" }),
    setDimension: (dimension: number) => fetchApi("/api/omniverse/dimension", { method: "POST", body: JSON.stringify({ dimension }) }),
    paradox: (data: { source_dapp: string; action: string; amount?: number; branches?: number }) =>
      fetchApi<{ paradox_id: number; branches: { branch_id: string; timeline: string; outcome: number; probability: number; status: string }[]; proof_hash: string }>(
        "/api/omniverse/paradox/branch", { method: "POST", body: JSON.stringify(data) }
      ),
    paradoxList: () =>
      fetchApi<{ paradoxes: { id: number; source_dapp: string; action: string; amount: number; branches: { branch_id: string; timeline: string; probability: number; outcome: number; status: string }[]; collapsed: boolean; collapsed_branch: string | null }[] }>(
        "/api/omniverse/paradox/list"
      ),
    paradoxCollapse: (data: { paradox_id: number; branch_id: string }) =>
      fetchApi<{ collapsed: { timeline: string; outcome: number }; realm_applied: string; message: string }>(
        "/api/omniverse/paradox/collapse", { method: "POST", body: JSON.stringify(data) }
      ),
    chrono: () => fetchApi<{ events: { id: number; t: string; dapp: string; type: string; label: string; amount: number; rewindable: boolean }[]; depth: number; can_rewind: number }>("/api/omniverse/chrono/timeline"),
    rewind: (data?: { event_id?: number; event_type?: string; dapp?: string }) =>
      fetchApi("/api/omniverse/chrono/rewind", { method: "POST", body: JSON.stringify(data || {}) }),
    quantum: () => fetchApi<{ superposed: boolean; states: { realm: string; value: number; alt_low: number; alt_high: number }[] }>("/api/omniverse/quantum/superposition"),
    collapse: (observe: string) => fetchApi("/api/omniverse/quantum/collapse", { method: "POST", body: JSON.stringify({ observe }) }),
    entangle: () => fetchApi("/api/omniverse/quantum/entangle", { method: "POST" }),
    hive: () => fetchApi<{ collective_intelligence: number; nodes_online: number; consensus_latency_ms: number; shared_predictions: { asset: string; direction: string; confidence: number }[]; tagline: string }>("/api/omniverse/hive/mind"),
    resonance: (target: string) => fetchApi("/api/omniverse/resonance/sync", { method: "POST", body: JSON.stringify({ target }) }),
    omniExecute: (data: { actions: { dapp: string; action: string; params?: Record<string, unknown> }[]; dimension: number }) =>
      fetchApi<{ actions_executed: number; results: { dapp: string; action: string; status: string; detail?: string; tx?: string }[]; omega_fragment: string }>(
        "/api/omniverse/omni/execute", { method: "POST", body: JSON.stringify(data) }
      ),
    omega: () => fetchApi<{ tier: string; digest: string; algorithm: string; unreachable: boolean; attestations: string[] }>("/api/omniverse/omega/proof"),
  },
};

export const queryKeys = {
  health: ["health"],
  cefiAccount: ["cefi", "account"],
  cefiOrders: ["cefi", "orders"],
  cefiFraud: ["cefi", "fraud"],
  cefiCustody: ["cefi", "custody"],
  cefiStats: ["cefi", "stats"],
  cefiEarn: ["cefi", "earn"],
  defiWallet: (id: string) => ["defi", "wallet", id],
  defiStaking: ["defi", "staking"],
  defiPools: ["defi", "pools"],
  defiRelics: ["defi", "relics"],
  defiProposals: ["defi", "proposals"],
  defiTx: ["defi", "transactions"],
  defiStats: ["defi", "stats"],
  defiRisk: ["defi", "risk"],
  hybridBalances: ["hybrid", "balances"],
  identity: (id: string) => ["identity", id],
  marketListings: ["market", "listings"],
  agents: ["agents"],
  rewards: ["rewards"],
  supportTickets: ["support", "tickets"],
  tesslink: ["tesslink"],
  walletConfig: ["wallet", "config"],
  casinoWallet: ["casino", "wallet"],
  casinoHistory: ["casino", "history"],
  casinoFeed: ["casino", "feed"],
  casinoLeaderboard: ["casino", "leaderboard"],
  omniverseStatus: ["omniverse", "status"],
  paradoxList: ["omniverse", "paradox"],
  chronoTimeline: ["omniverse", "chrono"],
  quantumState: ["omniverse", "quantum"],
  hiveMind: ["omniverse", "hive"],
  omegaProof: ["omniverse", "omega"],
  analyticsOverview: ["analytics", "overview"],
  marketBarters: ["market", "barters"],
};
