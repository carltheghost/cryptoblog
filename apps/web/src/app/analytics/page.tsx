"use client";

import { useQuery } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function AnalyticsPage() {
  const { data: graph, isLoading: gLoading } = useQuery({ queryKey: queryKeys.tesslink, queryFn: () => api.storage.tesslink() });
  const { data: health } = useQuery({ queryKey: queryKeys.health, queryFn: () => api.health() });
  const { data: childChain } = useQuery({ queryKey: ["defi", "child-chain"], queryFn: () => api.defi.childChain() });
  const { data: cefiStats } = useQuery({ queryKey: queryKeys.cefiStats, queryFn: () => api.cefi.stats() });
  const { data: defiStats } = useQuery({ queryKey: queryKeys.defiStats, queryFn: () => api.defi.stats() });

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">Analytics & Tessalink</h1>
        <UnthinkablePanel dapp="analytics" action="hive-predict" compact />
      </div>
      <UnthinkablePanel dapp="analytics" action="omniscient-view" />

      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="Tessalink Hypergraph">
          {gLoading ? <LoadingSpinner className="py-4" /> : (
            <>
              <p className="text-xs text-[var(--text-muted)]">
                {graph?.nodes?.length || 0} nodes · {graph?.edges?.length || 0} edges
              </p>
              <div className="mt-3 max-h-64 overflow-y-auto scrollbar-thin space-y-2">
                {(graph?.edges || []).map((e, i) => (
                  <div key={i} className="rounded-lg bg-[rgba(0,0,0,0.2)] p-2 text-[10px]">
                    <span className="text-[var(--accent-cyan)]">{e.source}</span>
                    <span className="mx-1 text-[var(--text-muted)]">—{e.type}→</span>
                    <span className="text-[var(--accent-violet)]">{e.target}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </GlassPanel>

        <GlassPanel title="Network Health" variant="green">
          <div className="space-y-3 text-xs">
            <div className="flex justify-between"><span>API Status</span><span className="text-[var(--accent-green)]">{health?.status || "checking..."}</span></div>
            <div className="flex justify-between"><span>MGANGA Chain (PoA)</span><span className="text-[var(--accent-green)]">Active</span></div>
            <div className="flex justify-between"><span>MWANJESA Chain (PoS)</span><span className="text-[var(--accent-green)]">Active</span></div>
            <div className="flex justify-between"><span>{childChain?.name}</span><span className="text-[var(--accent-violet)]">{childChain?.validators} validators</span></div>
            <div className="flex justify-between"><span>CeFi 24H Volume</span><span>${((cefiStats?.volume_24h ?? 0) / 1e9).toFixed(2)}B</span></div>
            <div className="flex justify-between"><span>DeFi TVL</span><span>${((defiStats?.tvl ?? 0) / 1e9).toFixed(2)}B</span></div>
            <div className="flex justify-between"><span>DAG Finality</span><span className="text-[var(--accent-cyan)]">&lt; 1 sec</span></div>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
