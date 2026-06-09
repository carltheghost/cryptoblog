"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

export function StakingPanel() {
  const [data, setData] = useState({ staked_amount: 0, rewards: 0, apy: 12.84 });

  useEffect(() => { api.defi.staking().then(setData); }, []);

  const stake = async () => {
    await api.defi.stake({ amount: 100, lock_days: 30 });
    api.defi.staking().then(setData);
    alert("Staked 100 TRD!");
  };

  return (
    <GlassPanel title="Staking TRD" variant="violet">
      <p className="font-mono text-lg font-bold text-[var(--accent-violet)]">{data.staked_amount.toLocaleString()} TRD</p>
      <p className="text-xs text-[var(--accent-green)]">{data.apy}% APY</p>
      <p className="mt-1 text-[10px] text-[var(--text-muted)]">Rewards: {data.rewards.toFixed(2)} TRD</p>
      <button onClick={stake} className="mt-2 w-full rounded-lg bg-[var(--accent-violet)] py-2 text-xs font-bold text-white">Stake More</button>
    </GlassPanel>
  );
}

export function DaoVote() {
  const [proposals, setProposals] = useState<{ id: number; title: string; votes_for: number; votes_against: number }[]>([]);

  useEffect(() => { api.defi.proposals().then(setProposals); }, []);

  const vote = async (id: number, support: boolean) => {
    await api.defi.vote({ proposal_id: id, support });
    api.defi.proposals().then(setProposals);
  };

  return (
    <GlassPanel title="DAO Vote" variant="violet">
      {proposals.map((p) => (
        <div key={p.id} className="mb-2 text-xs">
          <p className="font-semibold text-white">{p.title}</p>
          <div className="mt-1 flex gap-2 text-[10px] text-[var(--text-muted)]">
            <span className="text-[var(--accent-green)]">For: {p.votes_for}</span>
            <span className="text-[var(--accent-red)]">Against: {p.votes_against}</span>
          </div>
          <div className="mt-1 flex gap-1">
            <button onClick={() => vote(p.id, true)} className="flex-1 rounded bg-[rgba(0,255,136,0.15)] py-1 text-[var(--accent-green)]">Yes</button>
            <button onClick={() => vote(p.id, false)} className="flex-1 rounded bg-[rgba(255,68,102,0.15)] py-1 text-[var(--accent-red)]">No</button>
          </div>
        </div>
      ))}
    </GlassPanel>
  );
}
