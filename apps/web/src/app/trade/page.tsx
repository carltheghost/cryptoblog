"use client";

import { SpotTrading } from "@/components/cefi/spot-trading";
import { OrderBook } from "@/components/cefi/order-book";
import { DexSwap } from "@/components/defi/wallet-swap";
import { DefiPools } from "@/components/defi/pools-relics-bridge";
import { usePlatformStore } from "@/store/platform";
import { GlassPanel } from "@/components/ui/glass-panel";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";
import { OpenOrders } from "@/components/cefi/open-orders";
import { useQuery } from "@tanstack/react-query";
import { api, queryKeys } from "@/lib/api";

function PoolDepth() {
  const { data: pools } = useQuery({ queryKey: queryKeys.defiPools, queryFn: () => api.defi.pools() });
  const total = (pools || []).reduce((s, p) => s + p.tvl, 0) || 1;
  return (
    <GlassPanel title="Pool Depth" variant="violet">
      <div className="space-y-1 text-xs font-mono">
        {(pools || []).map((p) => (
          <div key={p.pair} className="flex justify-between text-[var(--text-muted)]">
            <span>{p.pair}</span>
            <span className="text-[var(--accent-violet)]">{((p.tvl / total) * 100).toFixed(1)}%</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export default function TradePage() {
  const { mode } = usePlatformStore();

  return (
    <div className="mx-auto max-w-6xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">TessExchange</h1>
        <UnthinkablePanel dapp="trade" action="paradox-order" compact />
      </div>
      <UnthinkablePanel dapp="trade" action="temporal-arbitrage" />
      {mode === "centralized" ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="md:col-span-2 space-y-4">
            <SpotTrading />
            <OpenOrders />
          </div>
          <OrderBook />
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div className="md:col-span-2"><DexSwap /></div>
          <div className="space-y-4">
            <PoolDepth />
            <DefiPools />
          </div>
        </div>
      )}
    </div>
  );
}
