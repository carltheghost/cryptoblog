const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
async function fetchApi<T = any>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(`API error: ${res.status}`);
  return res.json();
}

export const api = {
  health: () => fetchApi<{ status: string }>("/api/health"),
  cefi: {
    account: () => fetchApi("/api/cefi/account"),
    orderbook: (pair: string) => fetchApi(`/api/cefi/orderbook/${pair}`),
    ticker: () => fetchApi("/api/cefi/ticker"),
    chart: (pair: string) => fetchApi(`/api/cefi/chart/${pair}`),
    orders: () => fetchApi("/api/cefi/orders"),
    placeOrder: (data: object) => fetchApi("/api/cefi/orders", { method: "POST", body: JSON.stringify(data) }),
    fiatDeposit: (data: object) => fetchApi("/api/cefi/fiat/deposit", { method: "POST", body: JSON.stringify(data) }),
    compliance: () => fetchApi("/api/cefi/compliance/status"),
    fraudScore: () => fetchApi("/api/cefi/fraud-score"),
    custody: () => fetchApi("/api/cefi/custody"),
    stats: () => fetchApi("/api/cefi/stats"),
  },
  defi: {
    wallet: (tessId: string) => fetchApi(`/api/defi/wallet/${tessId}`),
    swapQuote: (data: object) => fetchApi("/api/defi/swap/quote", { method: "POST", body: JSON.stringify(data) }),
    swapExecute: (data: object) => fetchApi("/api/defi/swap/execute", { method: "POST", body: JSON.stringify(data) }),
    staking: () => fetchApi("/api/defi/staking"),
    stake: (data: object) => fetchApi("/api/defi/stake", { method: "POST", body: JSON.stringify(data) }),
    proposals: () => fetchApi("/api/defi/dao/proposals"),
    vote: (data: object) => fetchApi("/api/defi/dao/vote", { method: "POST", body: JSON.stringify(data) }),
    pools: () => fetchApi("/api/defi/pools"),
    relics: () => fetchApi("/api/defi/relics"),
    mintRelic: (data: object) => fetchApi("/api/defi/relics/mint", { method: "POST", body: JSON.stringify(data) }),
    bridge: (data: object) => fetchApi("/api/defi/bridge", { method: "POST", body: JSON.stringify(data) }),
    childChain: () => fetchApi("/api/defi/child-chain"),
  },
  identity: {
    get: (tessId: string) => fetchApi(`/api/identity/${tessId}`),
    hybridBalances: () => fetchApi("/api/identity/hybrid/balances"),
  },
  market: {
    listings: () => fetchApi("/api/market/listings"),
    createListing: (data: object) => fetchApi("/api/market/listings", { method: "POST", body: JSON.stringify(data) }),
    purchase: (id: number) => fetchApi(`/api/market/purchase/${id}`, { method: "POST" }),
  },
  agents: {
    list: () => fetchApi("/api/agents/"),
    get: (id: number) => fetchApi(`/api/agents/${id}`),
    create: (data: object) => fetchApi("/api/agents/", { method: "POST", body: JSON.stringify(data) }),
  },
  storage: {
    tesslink: () => fetchApi("/api/storage/tesslink/graph"),
    shadowProof: (tokenId: string) => fetchApi(`/api/storage/shadow-proof/${tokenId}`, { method: "POST" }),
  },
};
