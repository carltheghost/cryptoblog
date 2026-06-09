"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function RewardsPage() {
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: queryKeys.rewards, queryFn: () => api.rewards.get() });

  const claim = async () => {
    await toastAction(() => api.rewards.claim(), {
      loading: "Claiming rewards...",
      success: (r) => `Claimed ${(r as { claimed: number }).claimed} TRD!`,
    });
    qc.invalidateQueries({ queryKey: queryKeys.rewards });
    qc.invalidateQueries({ queryKey: queryKeys.defiWallet("TRD-8F7C-29D1") });
    qc.invalidateQueries({ queryKey: queryKeys.defiStaking });
    qc.invalidateQueries({ queryKey: queryKeys.cefiEarn });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  if (isLoading) return <LoadingSpinner />;

  const pools = data?.pools || [];

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">Rewards</h1>
        <div className="flex gap-2">
          <UnthinkablePanel dapp="rewards" action="infinite-yield" compact />
          <button onClick={claim} className="btn-primary btn-cefi">Claim {(data?.total_claimable ?? 0).toFixed(2)} TRD</button>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-4">
        {pools.map((p, i) => (
          <GlassPanel key={p.name} variant={i === 2 ? "gold" : i === 1 ? "violet" : "default"}>
            <h3 className="text-sm font-semibold text-[var(--text-muted)]">{p.name}</h3>
            <p className="mt-2 text-2xl font-bold text-[var(--accent-cyan)]">{p.amount.toLocaleString()} {p.token}</p>
            <p className="mt-1 text-xs text-[var(--text-muted)]">{p.description}</p>
          </GlassPanel>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="CeFi Earn APY"><p className="text-3xl font-bold text-[var(--accent-gold)]">{data?.cefi_earn_apy ?? 0}%</p></GlassPanel>
        <GlassPanel title="DeFi Staking APY" variant="violet"><p className="text-3xl font-bold text-[var(--accent-violet)]">{data?.defi_staking_apy ?? 0}%</p></GlassPanel>
      </div>
    </div>
  );
}
