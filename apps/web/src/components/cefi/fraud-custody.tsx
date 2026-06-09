"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";

export function FraudScore() {
  const { data, isLoading } = useQuery({ queryKey: queryKeys.cefiFraud, queryFn: () => api.cefi.fraudScore() });
  if (isLoading || !data) return <GlassPanel title="AI Fraud Score"><LoadingSpinner className="py-4" /></GlassPanel>;

  const pct = data.score as number;
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;
  const factors = data.factors;

  return (
    <GlassPanel title="AI Fraud Score" className="animate-fade-in">
      <div className="flex items-center gap-4">
        <div className="relative h-24 w-24 shrink-0">
          <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(0,242,255,0.1)" strokeWidth="8" />
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--accent-cyan)" strokeWidth="8"
              strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" className="transition-all duration-700" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold text-[var(--accent-cyan)]">{pct}</span>
            <span className="text-[8px] text-[var(--text-muted)]">/100</span>
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-[var(--accent-green)]">{data.recommendation as string}</p>
          <div className="mt-2 space-y-1">
            {factors?.map((f) => (
              <div key={f.name} className="flex items-center justify-between gap-4 text-[10px]">
                <span className="text-[var(--text-muted)]">{f.name}</span>
                <span className="text-[var(--accent-cyan)]">{f.score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

export function CustodyVault() {
  const { data, isLoading } = useQuery({ queryKey: queryKeys.cefiCustody, queryFn: () => api.cefi.custody() });
  if (isLoading || !data) return <GlassPanel title="Custody Vault"><LoadingSpinner className="py-4" /></GlassPanel>;
  const allocations = data.allocations;

  return (
    <GlassPanel title="Custody Vault" className="animate-fade-in">
      <p className="mb-2 text-[10px] uppercase tracking-wider text-[var(--accent-gold)]">Institutional Grade Cold Storage</p>
      <div className="space-y-1 text-xs">
        {allocations.map((a) => (
          <div key={a.asset} className="flex justify-between">
            <span className="font-semibold">{a.asset}</span>
            <span className="font-mono text-[var(--text-muted)]">{a.amount.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function CefiStats() {
  const { data } = useQuery({ queryKey: queryKeys.cefiStats, queryFn: () => api.cefi.stats() });
  const fmt = (n: number) => n >= 1e9 ? `$${(n / 1e9).toFixed(2)}B` : n.toLocaleString();

  return (
    <GlassPanel title="CeFi Network" className="animate-fade-in">
      <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
        <div><p className="text-[var(--text-muted)]">24H Volume</p><p className="font-bold">{fmt(data?.volume_24h ?? 0)}</p></div>
        <div><p className="text-[var(--text-muted)]">Open Interest</p><p className="font-bold">{fmt(data?.open_interest ?? 0)}</p></div>
        <div><p className="text-[var(--text-muted)]">Users Online</p><p className="font-bold">{(data?.users_online ?? 0).toLocaleString()}</p></div>
        <div><p className="text-[var(--text-muted)]">Uptime</p><p className="font-bold text-[var(--accent-green)]">{data?.uptime ?? 0}%</p></div>
      </div>
    </GlassPanel>
  );
}

export function CefiEarn() {
  const qc = useQueryClient();
  const [amount, setAmount] = useState("500");
  const { data, isLoading } = useQuery({ queryKey: queryKeys.cefiEarn, queryFn: () => api.cefi.earn() });
  if (isLoading || !data) return <GlassPanel title="CeFi Earn"><LoadingSpinner className="py-4" /></GlassPanel>;

  const stake = async () => {
    const val = parseFloat(amount);
    if (!val || val <= 0) return;
    await toastAction(() => api.cefi.earnStake(val), { success: `Staked ${val} MGANGA in CeFi earn` });
    qc.invalidateQueries({ queryKey: queryKeys.cefiEarn });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  const claim = async () => {
    await toastAction(() => api.cefi.earnClaim(), { success: "CeFi earn rewards claimed" });
    qc.invalidateQueries({ queryKey: queryKeys.cefiEarn });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
  };

  return (
    <GlassPanel title="CeFi Earn" variant="gold" className="animate-fade-in">
      <p className="font-mono text-lg font-bold text-[var(--accent-gold)]">{data.staked_mganga.toLocaleString()} MGANGA staked</p>
      <p className="text-xs text-[var(--text-muted)]">Available: {data.available_mganga.toLocaleString()}</p>
      <p className="text-xs text-[var(--accent-green)]">{data.apy}% APY · Rewards: {data.rewards_accrued}</p>
      <div className="mt-2 flex gap-2">
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field flex-1" type="number" min="1" />
        <button onClick={stake} className="btn-primary btn-cefi">Stake</button>
        <button onClick={claim} className="btn-primary btn-defi">Claim</button>
      </div>
      <div className="mt-2 space-y-1 text-[10px]">
        {data.products.map((p) => (
          <div key={p.name} className="flex justify-between text-[var(--text-muted)]">
            <span>{p.name}</span><span className="text-[var(--accent-gold)]">{p.apy}%</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
