"use client";

import { SpotTrading } from "@/components/cefi/spot-trading";
import { OrderBook } from "@/components/cefi/order-book";
import { DexSwap } from "@/components/defi/wallet-swap";
import { DefiPools } from "@/components/defi/pools-relics-bridge";
import { usePlatformStore } from "@/store/platform";
import { GlassPanel } from "@/components/ui/glass-panel";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

function PoolDepth() {
  return (
    <GlassPanel title="Pool Depth" variant="violet">
      <div className="space-y-1 text-xs font-mono">
        {["TRD/USDC 18.4%", "ETH/USDC 12.1%", "MGANGA/USDT 8.7%"].map((l) => (
          <div key={l} className="flex justify-between text-[var(--text-muted)]">
            <span>{l.split(" ")[0]}</span><span className="text-[var(--accent-violet)]">{l.split(" ")[1]}</span>
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
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2"><SpotTrading /></div>
          <OrderBook />
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2"><DexSwap /></div>
          <div className="space-y-4">
            <PoolDepth />
            <DefiPools />
          </div>
        </div>
      )}
    </div>
  );
}
