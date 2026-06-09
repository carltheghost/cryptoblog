"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";

export function StakingPanel() {
  const [amount, setAmount] = useState("100");
  const [busy, setBusy] = useState(false);
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: queryKeys.defiStaking, queryFn: () => api.defi.staking() });

  const stake = async () => {
    setBusy(true);
    const result = await toastAction(
      () => api.defi.stake({ amount: parseFloat(amount), lock_days: 30 }),
      { loading: "Staking...", success: (r) => `Staked ${(r as { staked: number }).staked} MWANJESA` }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: queryKeys.defiStaking });
      qc.invalidateQueries({ queryKey: ["defi", "wallet"] });
      qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    }
    setBusy(false);
  };

  const unstake = async () => {
    setBusy(true);
    const result = await toastAction(
      () => api.defi.unstake({ amount: parseFloat(amount), lock_days: 30 }),
      { loading: "Unstaking...", success: (r) => `Unstaked ${(r as { unstaked: number }).unstaked} TRD` }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: queryKeys.defiStaking });
      qc.invalidateQueries({ queryKey: ["defi", "wallet"] });
      qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    }
    setBusy(false);
  };

  if (isLoading) return <GlassPanel title="Staking TRD" variant="violet"><LoadingSpinner className="py-4" /></GlassPanel>;

  return (
    <GlassPanel title="Staking MWANJESA" variant="violet" className="animate-fade-in">
      <p className="font-mono text-lg font-bold text-[var(--accent-violet)]">{(data?.staked_amount ?? 0).toLocaleString()} staked</p>
      <p className="text-xs text-[var(--accent-green)]">{data?.apy ?? 0}% APY</p>
      <p className="mt-1 text-[10px] text-[var(--text-muted)]">Rewards: {(data?.rewards ?? 0).toFixed(2)} · Available: {(data?.available_balance ?? 0).toLocaleString()}</p>
      <div className="mt-2 flex gap-2">
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field flex-1" type="number" min="1" />
        <button onClick={stake} disabled={busy} className="btn-primary btn-defi">Stake</button>
        <button onClick={unstake} disabled={busy} className="btn-primary bg-[rgba(255,68,102,0.2)] text-[var(--accent-red)]">Unstake</button>
      </div>
    </GlassPanel>
  );
}

export function DaoVote() {
  const qc = useQueryClient();
  const { data: proposals, isLoading } = useQuery({ queryKey: queryKeys.defiProposals, queryFn: () => api.defi.proposals() });

  const vote = async (id: number, support: boolean) => {
    await toastAction(
      () => api.defi.vote({ proposal_id: id, support }),
      { success: `Vote recorded: ${support ? "Yes" : "No"}` }
    );
    qc.invalidateQueries({ queryKey: queryKeys.defiProposals });
  };

  if (isLoading) return <GlassPanel title="DAO Vote" variant="violet"><LoadingSpinner className="py-4" /></GlassPanel>;
  const list = proposals || [];

  return (
    <GlassPanel title="DAO Vote" variant="violet" className="animate-fade-in">
      {list.map((p) => (
        <div key={p.id} className="mb-2 text-xs">
          <p className="font-semibold">{p.title}</p>
          <div className="mt-1 flex gap-2 text-[10px]">
            <span className="text-[var(--accent-green)]">For: {p.votes_for}</span>
            <span className="text-[var(--accent-red)]">Against: {p.votes_against}</span>
          </div>
          <div className="mt-1 flex gap-1">
            <button onClick={() => vote(p.id, true)} className="flex-1 rounded bg-[rgba(0,255,136,0.15)] py-1 text-[var(--accent-green)] hover:bg-[rgba(0,255,136,0.25)]">Yes</button>
            <button onClick={() => vote(p.id, false)} className="flex-1 rounded bg-[rgba(255,68,102,0.15)] py-1 text-[var(--accent-red)] hover:bg-[rgba(255,68,102,0.25)]">No</button>
          </div>
        </div>
      ))}
    </GlassPanel>
  );
}
