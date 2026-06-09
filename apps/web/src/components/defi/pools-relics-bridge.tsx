"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { formatCompact } from "@/lib/utils";
import { toastAction } from "@/hooks/use-toast-action";

export function ChildChain() {
  const { data, isLoading } = useQuery({ queryKey: ["defi", "child-chain"], queryFn: () => api.defi.childChain() });
  if (isLoading) return <GlassPanel title="Child-Chain" variant="violet"><LoadingSpinner className="py-2" /></GlassPanel>;
  return (
    <GlassPanel title="Child-Chain" variant="violet" className="animate-fade-in">
      <p className="font-semibold text-[var(--accent-violet)]">{data?.name}</p>
      <div className="mt-1 flex justify-between text-xs text-[var(--text-muted)]">
        <span>TVL: {formatCompact(data?.tvl ?? 0)}</span>
        <span>{data?.block_time}s</span>
      </div>
    </GlassPanel>
  );
}

export function DefiPools() {
  const { data, isLoading } = useQuery({ queryKey: queryKeys.defiPools, queryFn: () => api.defi.pools() });
  if (isLoading) return <GlassPanel title="DeFi Pools" variant="violet"><LoadingSpinner className="py-2" /></GlassPanel>;
  const pools = data || [];
  return (
    <GlassPanel title="DeFi Pools" variant="violet" className="animate-fade-in">
      <div className="space-y-2 text-xs">
        {pools.map((p) => (
          <div key={p.pair} className="flex justify-between">
            <span className="font-semibold">{p.pair}</span>
            <span className="text-[var(--accent-green)]">{p.apy}% APY</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function DefiRiskScore() {
  const { data, isLoading } = useQuery({ queryKey: queryKeys.defiRisk, queryFn: () => api.defi.riskScore() });
  if (isLoading || !data) return <GlassPanel title="DeFi Risk Score" variant="violet"><LoadingSpinner className="py-4" /></GlassPanel>;
  const factors = data.factors;
  return (
    <GlassPanel title="DeFi Risk Score" variant="violet" className="animate-fade-in">
      <p className="text-2xl font-bold text-[var(--accent-violet)]">{data.score}<span className="text-sm text-[var(--text-muted)]">/100</span></p>
      <p className="text-xs text-[var(--accent-green)]">{data.recommendation}</p>
      <div className="mt-2 space-y-1">
        {factors?.map((f) => (
          <div key={f.name} className="flex justify-between text-[10px]">
            <span className="text-[var(--text-muted)]">{f.name}</span>
            <span className="text-[var(--accent-violet)]">{f.score}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function DefiStats() {
  const { data } = useQuery({ queryKey: queryKeys.defiStats, queryFn: () => api.defi.stats() });
  const fmt = (n: number) => n >= 1e9 ? `$${(n / 1e9).toFixed(2)}B` : `$${(n / 1e6).toFixed(0)}M`;
  return (
    <GlassPanel title="DeFi Network" variant="violet" className="animate-fade-in">
      <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
        <div><p className="text-[var(--text-muted)]">TVL</p><p className="font-bold">{fmt(data?.tvl as number || 0)}</p></div>
        <div><p className="text-[var(--text-muted)]">24H Vol</p><p className="font-bold">{fmt(data?.volume_24h as number || 0)}</p></div>
        <div><p className="text-[var(--text-muted)]">Pools</p><p className="font-bold">{data?.active_pools as number || 0}</p></div>
        <div><p className="text-[var(--text-muted)]">Avg APY</p><p className="font-bold text-[var(--accent-green)]">{data?.avg_apy as number || 0}%</p></div>
      </div>
    </GlassPanel>
  );
}

export function LivingRelicsGrid() {
  const { data, isLoading } = useQuery({ queryKey: queryKeys.defiRelics, queryFn: () => api.defi.relics() });
  if (isLoading) return <GlassPanel title="NFT / Game Assets" variant="violet"><LoadingSpinner className="py-4" /></GlassPanel>;
  const relics = data || [];
  return (
    <GlassPanel title="NFT / Game Assets" variant="violet" className="animate-fade-in">
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
        {relics.map((r) => (
          <div key={r.token_id} className="group overflow-hidden rounded-lg border border-[rgba(138,43,226,0.2)] transition-all hover:border-[var(--accent-violet)] hover:shadow-[0_0_15px_rgba(138,43,226,0.2)]">
            <img src={r.image_url} alt={r.name} className="h-16 w-full object-cover transition-transform group-hover:scale-105" />
            <p className="truncate px-1 py-1 text-[10px] font-semibold">{r.name}</p>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function CrossChainBridge() {
  const [amount, setAmount] = useState("500");
  const [token, setToken] = useState("USDC");
  const [busy, setBusy] = useState(false);
  const qc = useQueryClient();

  const bridge = async () => {
    setBusy(true);
    const result = await toastAction(
      () => api.defi.crossChain({ from_chain: "Ethereum", to_chain: "TribeChain", token, amount: parseFloat(amount) }),
      {
        loading: "Bridging assets...",
        success: (r) => `Bridged ${(r as { received: number }).received} ${token} to TribeChain`,
      }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: ["defi", "wallet"] });
      qc.invalidateQueries({ queryKey: queryKeys.defiTx });
    }
    setBusy(false);
  };

  return (
    <GlassPanel title="Cross-Chain Bridge" variant="violet" className="animate-fade-in">
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2 text-[var(--text-muted)]">
          <span>Ethereum</span><span className="text-[var(--accent-violet)]">→</span><span className="text-[var(--accent-violet)]">TribeChain</span>
        </div>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field" type="number" min="1" />
        <select value={token} onChange={(e) => setToken(e.target.value)} className="input-field">
          <option>USDC</option><option>ETH</option><option>TRD</option>
        </select>
        <button onClick={bridge} disabled={busy} className="btn-primary btn-defi w-full">Bridge Assets</button>
      </div>
    </GlassPanel>
  );
}
