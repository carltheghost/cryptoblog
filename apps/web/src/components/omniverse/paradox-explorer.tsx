"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GitBranch, X, Eye } from "lucide-react";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";
import { useOmniverseStore } from "@/store/omniverse";

type Branch = {
  branch_id: string;
  timeline: string;
  probability: number;
  outcome: number;
  status: string;
};

export function ParadoxExplorer({ open, onClose }: { open: boolean; onClose: () => void }) {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: queryKeys.paradoxList,
    queryFn: () => api.omniverse.paradoxList(),
    enabled: open,
  });

  const collapse = async (paradoxId: number, branchId: string) => {
    await toastAction(
      () => api.omniverse.paradoxCollapse({ paradox_id: paradoxId, branch_id: branchId }),
      { success: "Timeline collapsed — outcome applied to realm balances" }
    );
    qc.invalidateQueries({ queryKey: queryKeys.paradoxList });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/70 p-4 backdrop-blur-sm">
      <div className="max-h-[80vh] w-full max-w-lg overflow-hidden rounded-2xl border border-[var(--accent-red)] bg-[rgba(5,7,10,0.98)] shadow-[0_0_40px_rgba(255,68,102,0.3)]">
        <div className="flex items-center justify-between border-b border-[var(--border-glow)] px-4 py-3">
          <div className="flex items-center gap-2">
            <GitBranch className="h-4 w-4 text-[var(--accent-red)]" />
            <span className="text-sm font-black text-[var(--accent-red)]">PARADOX EXPLORER</span>
          </div>
          <button onClick={onClose} className="text-[var(--text-muted)] hover:text-white">
            <X className="h-4 w-4" />
          </button>
        </div>
        <div className="max-h-[60vh] space-y-3 overflow-y-auto p-4 scrollbar-thin">
          {(data?.paradoxes || []).length === 0 && (
            <p className="text-center text-xs text-[var(--text-muted)]">No paradox branches yet — spawn one from any DApp</p>
          )}
          {(data?.paradoxes || []).map((p) => (
            <div key={p.id} className="rounded-lg border border-[rgba(255,68,102,0.2)] bg-[rgba(0,0,0,0.4)] p-3">
              <div className="flex justify-between text-[10px]">
                <span className="font-bold uppercase text-[var(--accent-cyan)]">{p.source_dapp}</span>
                <span className="text-[var(--text-muted)]">{p.action}</span>
                {p.collapsed && <span className="text-[var(--accent-green)]">COLLAPSED</span>}
              </div>
              <div className="mt-2 grid gap-1">
                {p.branches.map((b) => (
                  <button
                    key={b.branch_id}
                    disabled={p.collapsed}
                    onClick={() => collapse(p.id, b.branch_id)}
                    className={cn(
                      "flex items-center justify-between rounded px-2 py-1.5 text-[9px] transition-all",
                      b.status === "collapsed" || b.status === "primary" && p.collapsed
                        ? "bg-[rgba(0,255,136,0.15)] text-[var(--accent-green)]"
                        : b.status === "annihilated"
                          ? "bg-[rgba(0,0,0,0.3)] text-[var(--text-muted)] line-through opacity-50"
                          : "bg-[rgba(255,68,102,0.1)] hover:bg-[rgba(255,68,102,0.25)] text-white"
                    )}
                  >
                    <span>Timeline {b.timeline} · {b.probability}%</span>
                    <span className="font-mono">{b.outcome >= 0 ? "+" : ""}{b.outcome}</span>
                    {!p.collapsed && <Eye className="h-3 w-3 text-[var(--accent-gold)]" />}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ParadoxExplorerTrigger() {
  const [open, setOpen] = useState(false);
  const paradoxCount = useOmniverseStoreCount();

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-1 rounded border border-[var(--accent-red)] px-2 py-1 text-[9px] text-[var(--accent-red)] hover:bg-[rgba(255,68,102,0.15)]"
      >
        <GitBranch className="h-3 w-3" />
        PX{paradoxCount > 0 ? ` ${paradoxCount}` : ""}
      </button>
      <ParadoxExplorer open={open} onClose={() => setOpen(false)} />
    </>
  );
}

function useOmniverseStoreCount() {
  return useOmniverseStore((s) => s.paradoxCount);
}
