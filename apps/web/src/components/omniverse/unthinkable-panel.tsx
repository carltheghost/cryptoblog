"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Atom, GitBranch, Zap, Eye } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";
import { getDappAction } from "@/components/omniverse/dapp-actions";
import { ParadoxExplorer } from "@/components/omniverse/paradox-explorer";
import { useOmniverseStore } from "@/store/omniverse";

export function UnthinkablePanel({
  dapp,
  action: actionOverride,
  compact = false,
}: {
  dapp: string;
  action?: string;
  compact?: boolean;
}) {
  const qc = useQueryClient();
  const [amount, setAmount] = useState("100");
  const [showParadox, setShowParadox] = useState(false);
  const dappMeta = getDappAction(dapp);
  const action = actionOverride || dappMeta.action;
  const { dimension } = useOmniverseStore();
  const { data: status } = useQuery({ queryKey: queryKeys.omniverseStatus, queryFn: () => api.omniverse.status() });

  const paradox = async () => {
    const res = await toastAction(
      () => api.omniverse.paradox({
        source_dapp: dapp,
        action,
        amount: parseFloat(amount) || dappMeta.amount || 0,
        branches: dimension >= 5 ? 5 : 3,
      }),
      { success: "Parallel realities spawned — open Paradox Explorer to collapse" }
    );
    if (res) setShowParadox(true);
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
    qc.invalidateQueries({ queryKey: queryKeys.paradoxList });
  };

  const resonate = async () => {
    await toastAction(() => api.omniverse.resonance(dapp), { success: "Soul resonance synced across all DApps" });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  const dappPulse = async () => {
    await toastAction(
      () => api.omniverse.omniExecute({
        dimension,
        actions: [{ dapp, action: dappMeta.omniAction, params: { amount: parseFloat(amount) || dappMeta.amount || 10 } }],
      }),
      { success: `${dappMeta.label} executed in ${dimension}D` }
    );
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
  };

  if (compact) {
    return (
      <>
        <div className="flex gap-1">
          <button onClick={paradox} title={dappMeta.label} className="rounded bg-[rgba(255,68,102,0.15)] px-2 py-1 text-[9px] text-[var(--accent-red)] hover:bg-[rgba(255,68,102,0.3)]">
            <GitBranch className="inline h-3 w-3" /> PX
          </button>
          <button onClick={dappPulse} title={dappMeta.omniAction} className="rounded bg-[rgba(0,242,255,0.15)] px-2 py-1 text-[9px] text-[var(--accent-cyan)] hover:bg-[rgba(0,242,255,0.3)]">
            <Zap className="inline h-3 w-3" /> ⚡
          </button>
          <button onClick={resonate} title="Soul Resonance" className="rounded bg-[rgba(138,43,226,0.15)] px-2 py-1 text-[9px] text-[var(--accent-violet)] hover:bg-[rgba(138,43,226,0.3)]">
            <Atom className="inline h-3 w-3" /> ♡
          </button>
        </div>
        <ParadoxExplorer open={showParadox} onClose={() => setShowParadox(false)} />
      </>
    );
  }

  return (
    <>
      <GlassPanel
        title={`◈ ${dappMeta.label}`}
        variant="gold"
        className={cn("border-dashed", status?.overdrive && "overdrive-border")}
        action={
          <button onClick={() => setShowParadox(true)} className="text-[8px] text-[var(--accent-red)] hover:underline">
            <Eye className="inline h-3 w-3" /> Explorer
          </button>
        }
      >
        <p className="text-[9px] text-[var(--text-muted)]">{dappMeta.description}</p>
        <div className="mt-2 grid grid-cols-3 gap-1 text-center text-[9px]">
          <div><p className="text-[var(--text-muted)]">Paradox</p><p className="font-bold text-[var(--accent-red)]">{status?.paradox_count ?? 0}</p></div>
          <div><p className="text-[var(--text-muted)]">Resonance</p><p className="font-bold text-[var(--accent-violet)]">{status?.soul_resonance ?? 0}%</p></div>
          <div><p className="text-[var(--text-muted)]">Ω Index</p><p className="font-bold text-[var(--accent-cyan)]">{status?.impossibility_index ?? 0}</p></div>
        </div>
        <div className="mt-2 flex gap-1">
          <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field flex-1 text-[10px]" type="number" />
          <button onClick={paradox} className="btn-primary bg-[rgba(255,68,102,0.2)] text-[var(--accent-red)] text-[9px] px-2">
            <GitBranch className="inline h-3 w-3" /> Branch
          </button>
          <button onClick={dappPulse} className="btn-primary text-[9px] px-2">
            <Zap className="inline h-3 w-3" /> Pulse
          </button>
          <button onClick={resonate} className="btn-primary btn-defi text-[9px] px-2">
            <Atom className="inline h-3 w-3" /> Sync
          </button>
        </div>
      </GlassPanel>
      <ParadoxExplorer open={showParadox} onClose={() => setShowParadox(false)} />
    </>
  );
}

export function OmniExecuteBar({ dapps }: { dapps: string[] }) {
  const qc = useQueryClient();
  const { dimension } = useOmniverseStore();
  const fire = async () => {
    const actions = dapps.map((d) => {
      const meta = getDappAction(d);
      return { dapp: d, action: meta.omniAction, params: { amount: meta.amount || 10 + dimension } };
    });
    const res = await toastAction(
      () => api.omniverse.omniExecute({ dimension, actions }),
      { success: (r) => `Omni-executed ${(r as { actions_executed: number }).actions_executed}/${dapps.length} real DApp actions` }
    );
    if (res) {
      qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
      qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
      qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
      qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
      qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
      qc.invalidateQueries({ queryKey: queryKeys.defiStaking });
      qc.invalidateQueries({ queryKey: queryKeys.rewards });
    }
  };
  return (
    <button onClick={fire} className="btn-primary w-full bg-gradient-to-r from-[var(--accent-cyan)] via-[var(--accent-violet)] to-[var(--accent-gold)] text-[10px] text-black font-black">
      <Zap className="inline h-3 w-3" /> OMNI-EXECUTE {dapps.length} DAPPS — REAL CROSS-CHAIN SAGA
    </button>
  );
}
