"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function AgentsPage() {
  const qc = useQueryClient();
  const [filter, setFilter] = useState<"all" | "administrative" | "autonomous">("all");
  const [selected, setSelected] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [form, setForm] = useState({ name: "", agent_type: "autonomous", description: "", budget: "100" });

  const { data: agents, isLoading } = useQuery({ queryKey: queryKeys.agents, queryFn: () => api.agents.list() });
  const { data: detail } = useQuery({
    queryKey: ["agents", selected],
    queryFn: () => api.agents.get(selected!),
    enabled: !!selected,
  });

  const filtered = (agents || []).filter((a) => filter === "all" || a.type === filter);

  const create = async () => {
    await toastAction(
      () => api.agents.create({ ...form, budget: parseFloat(form.budget) }),
      { success: `Agent "${form.name}" deployed!` }
    );
    setShowCreate(false);
    qc.invalidateQueries({ queryKey: queryKeys.agents });
  };

  const execute = async (id: number) => {
    await toastAction(
      () => api.agents.execute(id),
      { success: (r) => (r as { detail: string }).detail }
    );
    qc.invalidateQueries({ queryKey: queryKeys.agents });
    qc.invalidateQueries({ queryKey: ["agents", id] });
    qc.invalidateQueries({ queryKey: queryKeys.cefiOrders });
    qc.invalidateQueries({ queryKey: queryKeys.defiRelics });
  };

  const perf = detail?.performance;

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-violet">TessAgents</h1>
        <div className="flex gap-2">
          {(["all", "administrative", "autonomous"] as const).map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={cn("rounded-lg px-3 py-1 text-xs capitalize transition-all", filter === f ? "bg-[var(--accent-violet)] text-white" : "text-[var(--text-muted)] hover:text-white")}>{f}</button>
          ))}
          <UnthinkablePanel dapp="agents" action="neural-mesh" compact />
          <button onClick={() => setShowCreate(!showCreate)} className="btn-primary btn-defi ml-2">+ Deploy Agent</button>
        </div>
      </div>

      {showCreate && (
        <GlassPanel title="Deploy New Agent" variant="violet">
          <div className="grid grid-cols-2 gap-2 text-sm">
            <input placeholder="Agent Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field" />
            <select value={form.agent_type} onChange={(e) => setForm({ ...form, agent_type: e.target.value })} className="input-field">
              <option value="autonomous">Autonomous</option>
              <option value="administrative">Administrative</option>
            </select>
            <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field col-span-2 min-h-[60px]" />
            <input placeholder="Budget (MGANGA)" value={form.budget} onChange={(e) => setForm({ ...form, budget: e.target.value })} className="input-field" type="number" />
            <button onClick={create} className="btn-primary btn-defi">Deploy</button>
          </div>
        </GlassPanel>
      )}

      {isLoading ? <LoadingSpinner /> : (
        <div className="grid grid-cols-2 gap-4">
          {filtered.map((a) => (
            <GlassPanel
              key={a.id}
              variant={a.type === "administrative" ? "default" : "violet"}
              className={cn("cursor-pointer transition-all", selected === a.id && "ring-1 ring-[var(--accent-violet)]")}
              action={
                <div className="flex gap-2">
                  <button onClick={() => execute(a.id)} className="text-[10px] text-[var(--accent-cyan)] hover:underline">Run</button>
                  <button onClick={() => setSelected(selected === a.id ? null : a.id)} className="text-[10px] text-[var(--text-muted)]">{selected === a.id ? "Close" : "Details"}</button>
                </div>
              }
            >
              <h3 className="font-semibold">{a.name}</h3>
              <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)]">{a.type}</span>
              <p className="mt-2 text-xs text-[var(--text-muted)]">{a.description}</p>
              <div className="mt-3 flex gap-4 text-[10px]">
                <span>Budget: <span className="text-[var(--accent-cyan)]">{a.budget}</span></span>
                <span>Stake: <span className="text-[var(--accent-violet)]">{a.stake}</span></span>
                <span className={a.status === "active" ? "text-[var(--accent-green)]" : "text-[var(--text-muted)]"}>{a.status}</span>
              </div>
              {selected === a.id && perf && (
                <div className="mt-3 border-t border-[var(--border-glow)] pt-3 text-[10px] animate-fade-in">
                  <p>Tasks: {perf.tasks_completed} · Accuracy: {perf.accuracy}% · Earnings: {perf.earnings} MGANGA</p>
                </div>
              )}
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
