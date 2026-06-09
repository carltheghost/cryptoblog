"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

export default function AnalyticsPage() {
  const [graph, setGraph] = useState<{ nodes: { id: string; type: string }[]; edges: { source: string; target: string; type: string }[] }>({ nodes: [], edges: [] });

  useEffect(() => { api.storage.tesslink().then(setGraph); }, []);

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Analytics & Tessalink</h1>
      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="Tessalink Hypergraph">
          <p className="text-xs text-[var(--text-muted)]">{graph.nodes.length} nodes · {graph.edges.length} edges</p>
          <div className="mt-2 max-h-48 overflow-y-auto space-y-1 text-[10px]">
            {graph.edges.map((e, i) => (
              <div key={i} className="text-[var(--text-muted)]">
                <span className="text-[var(--accent-cyan)]">{e.source}</span> → <span className="text-[var(--accent-violet)]">{e.target}</span> ({e.type})
              </div>
            ))}
          </div>
        </GlassPanel>
        <GlassPanel title="Network Health" variant="green">
          <div className="space-y-2 text-xs">
            <div className="flex justify-between"><span>MGANGA Chain (PoA)</span><span className="text-[var(--accent-green)]">Active</span></div>
            <div className="flex justify-between"><span>MWANJESA Chain (PoS)</span><span className="text-[var(--accent-green)]">Active</span></div>
            <div className="flex justify-between"><span>HYB Bridge</span><span className="text-[var(--accent-green)]">Operational</span></div>
            <div className="flex justify-between"><span>DAG Tessalink</span><span className="text-[var(--accent-cyan)]">{"< 1s finality"}</span></div>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
