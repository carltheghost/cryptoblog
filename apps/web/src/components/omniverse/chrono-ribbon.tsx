"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Rewind, Clock } from "lucide-react";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";

const DAPP_COLORS: Record<string, string> = {
  cefi: "text-[var(--accent-cyan)]",
  defi: "text-[var(--accent-violet)]",
  casino: "text-[var(--accent-gold)]",
  omniverse: "text-[var(--accent-red)]",
};

type ChronoEvent = {
  id: number;
  t: string;
  dapp: string;
  type: string;
  label: string;
  amount: number;
  rewindable: boolean;
};

export function ChronoRibbon() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: queryKeys.chronoTimeline,
    queryFn: () => api.omniverse.chrono(),
    refetchInterval: 15000,
  });

  const rewindEvent = async (e: ChronoEvent) => {
    if (!e.rewindable) return;
    await toastAction(
      () => api.omniverse.rewind({ event_id: e.id, event_type: e.type, dapp: e.dapp }),
      { success: `Rewound ${e.dapp} event — causality restored` }
    );
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
    qc.invalidateQueries({ queryKey: queryKeys.cefiOrders });
  };

  const rewindAll = async () => {
    await toastAction(() => api.omniverse.rewind({}), { success: "Global timeline pulse — stability +%" });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  const events = (data?.events?.slice(0, 10) || []) as ChronoEvent[];

  return (
    <div className="chrono-ribbon border-t border-[var(--border-glow)] bg-[rgba(5,7,10,0.98)] px-3 py-1.5">
      <div className="flex items-center gap-3">
        <div className="flex shrink-0 items-center gap-1 text-[9px] text-[var(--text-muted)]">
          <Clock className="h-3 w-3" />
          <span>CHRONO</span>
          <span className="text-[var(--accent-cyan)]">{data?.can_rewind ?? 0}↩</span>
          <button onClick={rewindAll} className="ml-1 rounded bg-[rgba(0,242,255,0.1)] px-1.5 py-0.5 text-[var(--accent-cyan)] hover:bg-[rgba(0,242,255,0.2)]">
            <Rewind className="inline h-2.5 w-2.5" /> Pulse
          </button>
        </div>
        <div className="flex flex-1 gap-2 overflow-x-auto scrollbar-thin">
          {events.map((e) => (
            <button
              key={`${e.dapp}-${e.id}-${e.t}`}
              onClick={() => e.rewindable && rewindEvent(e)}
              disabled={!e.rewindable}
              className={cn(
                "flex shrink-0 items-center gap-1 rounded px-2 py-0.5 text-[8px] transition-all",
                e.rewindable
                  ? "cursor-pointer bg-[rgba(0,242,255,0.08)] hover:bg-[rgba(0,242,255,0.2)] hover:ring-1 hover:ring-[var(--accent-cyan)]"
                  : "bg-[rgba(0,0,0,0.3)] opacity-70"
              )}
            >
              <span className={cn("font-bold uppercase", DAPP_COLORS[e.dapp] || "text-white")}>{e.dapp}</span>
              <span className="text-[var(--text-muted)]">{e.label}</span>
              {e.rewindable && <Rewind className="h-2.5 w-2.5 text-[var(--accent-gold)]" />}
            </button>
          ))}
          {events.length === 0 && <span className="text-[9px] text-[var(--text-muted)]">No timeline events — omni-execute or trade to populate Chrono</span>}
        </div>
      </div>
    </div>
  );
}
