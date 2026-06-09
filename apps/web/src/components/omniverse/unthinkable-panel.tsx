"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Atom, GitBranch, Eye, Zap, Infinity } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";

export function UnthinkablePanel({
  dapp,
  action = "pulse",
  compact = false,
}: {
  dapp: string;
  action?: string;
  compact?: boolean;
}) {
  const qc = useQueryClient();
  const [amount, setAmount] = useState("100");
  const { data: status } = useQuery({ queryKey: queryKeys.omniverseStatus, queryFn: () => api.omniverse.status() });

  const paradox = async () => {
    await toastAction(
      () => api.omniverse.paradox({ source_dapp: dapp, action, amount: parseFloat(amount) || 0, branches: 3 }),
      { success: "3 parallel realities spawned — paradox active" }
    );
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
  };

  const resonate = async () => {
    await toastAction(() => api.omniverse.resonance(dapp), { success: "Soul resonance synced across all DApps" });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  if (compact) {
    return (
      <div className="flex gap-1">
        <button onClick={paradox} title="Paradox Branch" className="rounded bg-[rgba(255,68,102,0.15)] px-2 py-1 text-[9px] text-[var(--accent-red)] hover:bg-[rgba(255,68,102,0.3)]">
          <GitBranch className="inline h-3 w-3" /> PX
        </button>
        <button onClick={resonate} title="Soul Resonance" className="rounded bg-[rgba(138,43,226,0.15)] px-2 py-1 text-[9px] text-[var(--accent-violet)] hover:bg-[rgba(138,43,226,0.3)]">
          <Atom className="inline h-3 w-3" /> ♡
        </button>
      </div>
    );
  }

  return (
    <GlassPanel
      title="◈ Unthinkable Layer"
      variant="gold"
      className={cn("border-dashed", status?.overdrive && "overdrive-border")}
      action={<span className="text-[8px] text-[var(--accent-gold)]">Ω{status?.impossibility_index ?? 0}</span>}
    >
      <p className="text-[9px] text-[var(--text-muted)]">Beyond human standard · Paradox · Quantum · Soul</p>
      <div className="mt-2 grid grid-cols-3 gap-1 text-center text-[9px]">
        <div><p className="text-[var(--text-muted)]">Paradox</p><p className="font-bold text-[var(--accent-red)]">{status?.paradox_count ?? 0}</p></div>
        <div><p className="text-[var(--text-muted)]">Resonance</p><p className="font-bold text-[var(--accent-violet)]">{status?.soul_resonance ?? 0}%</p></div>
        <div><p className="text-[var(--text-muted)]">Hive</p><p className="font-bold text-[var(--accent-cyan)]">{status?.hive_sync_percent ?? 0}%</p></div>
      </div>
      <div className="mt-2 flex gap-1">
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field flex-1 text-[10px]" type="number" />
        <button onClick={paradox} className="btn-primary bg-[rgba(255,68,102,0.2)] text-[var(--accent-red)] text-[9px] px-2">
          <GitBranch className="inline h-3 w-3" /> Branch
        </button>
        <button onClick={resonate} className="btn-primary btn-defi text-[9px] px-2">
          <Atom className="inline h-3 w-3" /> Sync
        </button>
      </div>
    </GlassPanel>
  );
}

export function OmniExecuteBar({ dapps }: { dapps: string[] }) {
  const qc = useQueryClient();
  const fire = async () => {
    await toastAction(
      () => api.omniverse.omniExecute({
        dimension: 5,
        actions: dapps.map((d) => ({ dapp: d, action: "pulse" })),
      }),
      { success: `Omni-executed across ${dapps.length} DApps in 5D singularity` }
    );
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };
  return (
    <button onClick={fire} className="btn-primary w-full bg-gradient-to-r from-[var(--accent-cyan)] via-[var(--accent-violet)] to-[var(--accent-gold)] text-[10px] text-black font-black">
      <Zap className="inline h-3 w-3" /> OMNI-EXECUTE {dapps.length} DAPPS SIMULTANEOUSLY
    </button>
  );
}
