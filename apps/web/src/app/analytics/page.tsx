"use client";

import { useQuery } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function AnalyticsPage() {
  const { data: graph, isLoading: gLoading } = useQuery({ queryKey: queryKeys.tesslink, queryFn: () => api.storage.tesslink() });
  const { data: health } = useQuery({ queryKey: queryKeys.health, queryFn: () => api.health() });
  const { data: overview, isLoading: oLoading } = useQuery({ queryKey: queryKeys.analyticsOverview, queryFn: () => api.analytics.overview(), refetchInterval: 30000 });
  const { data: childChain } = useQuery({ queryKey: ["defi", "child-chain"], queryFn: () => api.defi.childChain() });

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">Analytics & Tessalink</h1>
        <UnthinkablePanel dapp="analytics" action="hive-predict" compact />
      </div>
      <UnthinkablePanel dapp="analytics" action="omniscient-view" />

      {oLoading ? <LoadingSpinner /> : (
        <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
          {[
            { label: "24H Volume", value: `$${(overview?.volume_24h ?? 0).toLocaleString()}`, color: "text-[var(--accent-cyan)]" },
            { label: "CeFi Orders", value: overview?.orders_24h ?? 0, color: "text-[var(--accent-green)]" },
            { label: "Casino Bets", value: overview?.casino_bets_24h ?? 0, color: "text-[var(--accent-gold)]" },
            { label: "Pool TVL", value: `$${(overview?.pool_tvl ?? 0).toLocaleString()}`, color: "text-[var(--accent-violet)]" },
          ].map(({ label, value, color }) => (
            <GlassPanel key={label}>
              <p className="text-[10px] text-[var(--text-muted)]">{label}</p>
              <p className={`text-lg font-black ${color}`}>{value}</p>
            </GlassPanel>
          ))}
        </div>
      )}

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <GlassPanel title="Tessalink Hypergraph">
          {gLoading ? <LoadingSpinner className="py-4" /> : (
            <>
              <p className="text-xs text-[var(--text-muted)]">
                {graph?.nodes?.length || 0} nodes · {graph?.edges?.length || 0} edges · {overview?.tesslink_edges ?? 0} tracked
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
            {(overview?.chains || []).map((c) => (
              <div key={c.name} className="flex justify-between">
                <span>{c.name}</span>
                <span className="text-[var(--accent-green)]">{c.status} · {c.load}% load</span>
              </div>
            ))}
            <div className="flex justify-between"><span>{childChain?.name}</span><span className="text-[var(--accent-violet)]">{childChain?.validators} validators</span></div>
            <div className="flex justify-between"><span>Bridge 24H</span><span>${(overview?.bridge_volume_24h ?? 0).toLocaleString()}</span></div>
            <div className="flex justify-between"><span>DeFi TX 24H</span><span>{overview?.defi_tx_24h ?? 0}</span></div>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
