export type DappAction = {
  label: string;
  action: string;
  description: string;
  omniAction: string;
  amount?: number;
};

export const DAPP_UNTHINKABLE: Record<string, DappAction> = {
  trade: {
    label: "Paradox Order",
    action: "paradox-order",
    description: "Spawn 3 order timelines — collapse one into CeFi book",
    omniAction: "ghost-order",
  },
  wallet: {
    label: "Quantum Vault",
    action: "quantum-vault",
    description: "Entangle multisig across CeFi/DeFi vault layers",
    omniAction: "vault-pulse",
  },
  casino: {
    label: "Probability Weave",
    action: "probability-weave",
    description: "Fork bet outcomes across parallel slot reels",
    omniAction: "omni-spin",
    amount: 15,
  },
  market: {
    label: "Barter Paradox",
    action: "barter-paradox",
    description: "List same asset in 3 timelines simultaneously",
    omniAction: "barter-scan",
  },
  assets: {
    label: "Superposition Holdings",
    action: "superposition-holdings",
    description: "Hold portfolio in Ψ until observed",
    omniAction: "micro-stake",
  },
  orders: {
    label: "Timeline Fork",
    action: "timeline-fork",
    description: "Split order history into rewindable branches",
    omniAction: "ghost-order",
  },
  analytics: {
    label: "Omniscient View",
    action: "omniscient-view",
    description: "Hive-mind aggregate beyond individual charts",
    omniAction: "neural-mesh",
  },
  relics: {
    label: "Soul Bind",
    action: "soul-bind",
    description: "Bind relic soul reserves to omniverse mesh",
    omniAction: "soul-bind",
  },
  agents: {
    label: "Neural Mesh",
    action: "neural-mesh",
    description: "Link agents into collective inference lattice",
    omniAction: "neural-mesh",
  },
  rewards: {
    label: "Infinite Yield",
    action: "infinite-yield",
    description: "Claim rewards across collapsed timelines",
    omniAction: "claim-pulse",
  },
  cefi: {
    label: "CeFi Pulse",
    action: "hybrid-pulse",
    description: "Stake MGANGA into earn across dimensions",
    omniAction: "earn-stake",
    amount: 25,
  },
  defi: {
    label: "DeFi Pulse",
    action: "temporal-arbitrage",
    description: "Micro-stake TRD in parallel DeFi pools",
    omniAction: "micro-stake",
    amount: 20,
  },
  support: {
    label: "Paradox Ticket",
    action: "paradox-ticket",
    description: "Open ticket in superposed support states",
    omniAction: "vault-pulse",
  },
  settings: {
    label: "Reality Config",
    action: "reality-config",
    description: "Tune dimension defaults and omega tier",
    omniAction: "vault-pulse",
  },
};

export function getDappAction(dapp: string): DappAction {
  return DAPP_UNTHINKABLE[dapp] || {
    label: "Omniverse Pulse",
    action: "pulse",
    description: "Cross-dimensional energy pulse",
    omniAction: "pulse",
  };
}
