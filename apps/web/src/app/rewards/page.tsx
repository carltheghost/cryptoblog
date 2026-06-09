"use client";

import { GlassPanel } from "@/components/ui/glass-panel";

export default function RewardsPage() {
  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Rewards</h1>
      <div className="grid grid-cols-3 gap-4">
        <GlassPanel title="Activity Pool"><p className="text-2xl font-bold text-[var(--accent-cyan)]">2,450 TRD</p><p className="text-xs text-[var(--text-muted)]">Earned from engagement</p></GlassPanel>
        <GlassPanel title="Trade Pool" variant="violet"><p className="text-2xl font-bold text-[var(--accent-violet)]">890 TRD</p><p className="text-xs text-[var(--text-muted)]">Trading fee rewards</p></GlassPanel>
        <GlassPanel title="Legacy Pool" variant="gold"><p className="text-2xl font-bold text-[var(--accent-gold)]">142 TRD</p><p className="text-xs text-[var(--text-muted)]">Staking rewards</p></GlassPanel>
      </div>
    </div>
  );
}
