"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Atom, Brain, Clock, GitBranch, Infinity, Shield, Zap } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { Hypercube4D } from "@/components/casino/hypercube-4d";
import { OmniExecuteBar } from "@/components/omniverse/unthinkable-panel";
import { DIMENSION_LABELS, useOmniverseStore } from "@/store/omniverse";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";

const ALL_DAPPS = ["cefi", "defi", "casino", "wallet", "market", "relics", "agents", "trade", "rewards"];

export default function OmniversePage() {
  const qc = useQueryClient();
  const { dimension } = useOmniverseStore();
  const { data: status, isLoading } = useQuery({ queryKey: queryKeys.omniverseStatus, queryFn: () => api.omniverse.status() });
  const { data: quantum } = useQuery({ queryKey: queryKeys.quantumState, queryFn: () => api.omniverse.quantum() });
  const { data: hive } = useQuery({ queryKey: queryKeys.hiveMind, queryFn: () => api.omniverse.hive() });
  const { data: omega } = useQuery({ queryKey: queryKeys.omegaProof, queryFn: () => api.omniverse.omega() });
  const { data: chrono } = useQuery({ queryKey: queryKeys.chronoTimeline, queryFn: () => api.omniverse.chrono() });

  const entangle = () => toastAction(() => api.omniverse.entangle(), { success: "Quantum entanglement active" }).then(() => qc.invalidateQueries({ queryKey: queryKeys.quantumState }));

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="mx-auto max-w-6xl space-y-6 animate-fade-in">
      <div className="relative overflow-hidden rounded-2xl border border-[var(--accent-gold)] bg-gradient-to-br from-[rgba(255,68,102,0.1)] via-[rgba(138,43,226,0.15)] to-[rgba(0,242,255,0.1)] p-8">
        <div className="absolute inset-0 dim-infinite-bg opacity-30" />
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-black">
              <span className="neon-text-gold">OMNIVERSE</span>
              <span className="ml-2 text-[var(--accent-violet)]">ENGINE</span>
            </h1>
            <p className="mt-2 text-sm text-[var(--text-muted)]">
              Unreachable tier · Impossibility Index <span className="font-mono text-[var(--accent-cyan)]">{status?.impossibility_index}</span>
              · Reality Stability {status?.reality_stability}%
            </p>
            <p className="mt-1 text-xs text-[var(--accent-gold)]">{DIMENSION_LABELS[dimension]} viewing active</p>
          </div>
          <Hypercube4D size={140} active />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {[
          { label: "Paradox Branches", value: status?.paradox_count, icon: GitBranch, color: "text-[var(--accent-red)]" },
          { label: "Soul Resonance", value: `${status?.soul_resonance}%`, icon: Atom, color: "text-[var(--accent-violet)]" },
          { label: "Hive Sync", value: `${status?.hive_sync_percent}%`, icon: Brain, color: "text-[var(--accent-cyan)]" },
          { label: "Chrono Depth", value: chrono?.depth ?? 0, icon: Clock, color: "text-[var(--accent-gold)]" },
        ].map(({ label, value, icon: Icon, color }) => (
          <GlassPanel key={label}>
            <Icon className={`h-5 w-5 ${color}`} />
            <p className="mt-2 text-2xl font-black">{value}</p>
            <p className="text-[10px] text-[var(--text-muted)]">{label}</p>
          </GlassPanel>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="Quantum Superposition" variant="violet">
          <p className="text-[10px] text-[var(--text-muted)]">Balances exist in multiple states until observed</p>
          <div className="mt-3 space-y-2">
            {(quantum?.states || []).map((s) => (
              <div key={s.realm} className="quantum-state-bar rounded-lg bg-[rgba(0,0,0,0.3)] p-2 text-[10px]">
                <div className="flex justify-between">
                  <span className="uppercase font-bold">{s.realm}</span>
                  <span className="font-mono">{s.value.toLocaleString()}</span>
                </div>
                <div className="mt-1 flex justify-between text-[var(--text-muted)]">
                  <span>Ψ low: {s.alt_low}</span>
                  <span>Ψ high: {s.alt_high}</span>
                </div>
              </div>
            ))}
          </div>
          <button onClick={entangle} className="btn-primary btn-defi mt-3 w-full text-[10px]">
            <Zap className="inline h-3 w-3" /> Re-Entangle All Realms
          </button>
        </GlassPanel>

        <GlassPanel title="Hive Mind Collective">
          <p className="text-[10px] text-[var(--text-muted)]">{hive?.tagline}</p>
          <p className="mt-2 text-3xl font-black text-[var(--accent-cyan)]">{hive?.collective_intelligence}%</p>
          <p className="text-[10px]">{hive?.nodes_online?.toLocaleString()} nodes · {hive?.consensus_latency_ms}ms consensus</p>
          <div className="mt-3 space-y-1 text-[10px]">
            {hive?.shared_predictions?.map((p) => (
              <div key={p.asset} className="flex justify-between">
                <span>{p.asset} → {p.direction}</span>
                <span className="text-[var(--accent-green)]">{p.confidence}%</span>
              </div>
            ))}
          </div>
        </GlassPanel>

        <GlassPanel title="RF-SAM-Ω Proof" variant="gold">
          <div className="flex items-center gap-2">
            <Shield className="h-5 w-5 text-[var(--accent-gold)]" />
            <span className="font-bold text-[var(--accent-gold)]">{omega?.tier}</span>
          </div>
          <p className="mt-2 font-mono text-[9px] break-all text-[var(--text-muted)]">{omega?.digest}</p>
          <p className="mt-2 text-[10px]">{omega?.algorithm}</p>
          <ul className="mt-2 space-y-0.5 text-[9px] text-[var(--text-muted)]">
            {omega?.attestations?.map((a) => <li key={a}>✓ {a}</li>)}
          </ul>
        </GlassPanel>

        <GlassPanel title="Chrono Ledger">
          <div className="max-h-40 space-y-1 overflow-y-auto scrollbar-thin text-[9px]">
            {(chrono?.events || []).map((e, i) => (
              <div key={i} className="flex justify-between rounded bg-[rgba(0,0,0,0.2)] px-2 py-1">
                <span className="text-[var(--accent-cyan)]">{e.dapp}</span>
                <span>{e.label}</span>
                {e.rewindable && <span className="text-[var(--accent-gold)]">↩</span>}
              </div>
            ))}
          </div>
        </GlassPanel>
      </div>

      <GlassPanel title="Omni-Executor — All DApps · One Singularity" variant="gold">
        <p className="mb-3 text-[10px] text-[var(--text-muted)]">
          Fire atomic pulses across every DApp simultaneously in 5D — something no human-standard platform can do
        </p>
        <div className="mb-3 flex flex-wrap gap-1">
          {ALL_DAPPS.map((d) => (
            <span key={d} className="rounded bg-[rgba(0,242,255,0.1)] px-2 py-0.5 text-[9px] uppercase text-[var(--accent-cyan)]">{d}</span>
          ))}
        </div>
        <OmniExecuteBar dapps={ALL_DAPPS} />
      </GlassPanel>

      <div className="text-center text-[10px] text-[var(--text-muted)]">
        <Infinity className="mx-auto mb-1 h-4 w-4 text-[var(--accent-gold)]" />
        Beyond human standard · Unreachable · Unthinkable · Unstoppable
      </div>
    </div>
  );
}
