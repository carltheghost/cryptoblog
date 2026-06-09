"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

interface Agent { id: number; name: string; type: string; description: string; status: string; budget: number; stake: number }

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filter, setFilter] = useState<"all" | "administrative" | "autonomous">("all");

  useEffect(() => { api.agents.list().then(setAgents); }, []);

  const filtered = filter === "all" ? agents : agents.filter((a) => a.type === filter);

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-violet">TessAgents</h1>
        <div className="flex gap-2">
          {(["all", "administrative", "autonomous"] as const).map((f) => (
            <button key={f} onClick={() => setFilter(f)} className={cn("rounded-lg px-3 py-1 text-xs capitalize", filter === f ? "bg-[var(--accent-violet)] text-white" : "text-[var(--text-muted)]")}>{f}</button>
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        {filtered.map((a) => (
          <GlassPanel key={a.id} variant={a.type === "administrative" ? "default" : "violet"}>
            <div className="flex items-start justify-between">
              <div>
                <h3 className="font-semibold text-white">{a.name}</h3>
                <span className="text-[10px] uppercase tracking-wider text-[var(--text-muted)]">{a.type}</span>
              </div>
              <span className={cn("rounded-full px-2 py-0.5 text-[10px]", a.status === "active" ? "bg-[rgba(0,255,136,0.15)] text-[var(--accent-green)]" : "text-[var(--text-muted)]")}>{a.status}</span>
            </div>
            <p className="mt-2 text-xs text-[var(--text-muted)]">{a.description}</p>
            <div className="mt-3 flex gap-4 text-[10px]">
              <span>Budget: <span className="text-[var(--accent-cyan)]">{a.budget} MGANGA</span></span>
              <span>Stake: <span className="text-[var(--accent-violet)]">{a.stake}</span></span>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}
