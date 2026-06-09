"use client";

import { useQuery } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { usePlatformStore } from "@/store/platform";
import { cn } from "@/lib/utils";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function OrdersPage() {
  const { mode } = usePlatformStore();
  const { data: cefiOrders, isLoading: cLoading } = useQuery({
    queryKey: queryKeys.cefiOrders,
    queryFn: () => api.cefi.orders(),
    enabled: mode === "centralized",
  });
  const { data: defiTx, isLoading: dLoading } = useQuery({
    queryKey: queryKeys.defiTx,
    queryFn: () => api.defi.transactions(),
    enabled: mode === "decentralized",
  });

  const isLoading = mode === "centralized" ? cLoading : dLoading;

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">
          {mode === "centralized" ? "CeFi Order History" : "DeFi Transaction History"}
        </h1>
        <UnthinkablePanel dapp="orders" action="chrono-trace" compact />
      </div>
      <UnthinkablePanel dapp="orders" action="timeline-fork" />

      {mode === "centralized" ? (
        <GlassPanel>
          {isLoading ? <LoadingSpinner className="py-4" /> : (
            <div className="space-y-2 text-xs">
              {(cefiOrders || []).length === 0 && (
                <p className="text-[var(--text-muted)]">No orders yet. Place one from the Trade page.</p>
              )}
              {(cefiOrders || []).map((o) => (
                <div key={o.id} className="flex items-center justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-3">
                  <span className="font-semibold">{o.pair}</span>
                  <span className={cn(o.side === "buy" ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>{o.side.toUpperCase()}</span>
                  <span className="font-mono">{o.price.toFixed(2)}</span>
                  <span>{o.amount}</span>
                  <span className="text-[var(--accent-green)]">{o.status}</span>
                </div>
              ))}
            </div>
          )}
        </GlassPanel>
      ) : (
        <GlassPanel variant="violet">
          {isLoading ? <LoadingSpinner className="py-4" /> : (
            <div className="space-y-2 text-xs">
              {(defiTx || []).length === 0 && (
                <p className="text-[var(--text-muted)]">No DeFi transactions yet. Swap, stake, or bridge to get started.</p>
              )}
              {(defiTx || []).map((t) => (
                <div key={t.id} className="flex items-center justify-between rounded-lg bg-[rgba(138,43,226,0.08)] p-3">
                  <span className="font-semibold capitalize">{t.type}</span>
                  <span className="text-[var(--text-muted)]">{t.from_token}{t.to_token ? ` → ${t.to_token}` : ""}</span>
                  <span>{t.amount}</span>
                  <span className="font-mono text-[10px] text-[var(--accent-violet)]">{t.tx_hash?.slice(0, 10)}...</span>
                  <span className="text-[var(--accent-green)]">{t.status}</span>
                </div>
              ))}
            </div>
          )}
        </GlassPanel>
      )}
    </div>
  );
}
