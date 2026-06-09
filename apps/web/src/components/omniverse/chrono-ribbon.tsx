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

export function ChronoRibbon() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: queryKeys.chronoTimeline,
    queryFn: () => api.omniverse.chrono(),
    refetchInterval: 15000,
  });

  const rewind = async () => {
    await toastAction(() => api.omniverse.rewind(), { success: "Timeline rewound — causality re-stitched" });
    qc.invalidateQueries({ queryKey: queryKeys.chronoTimeline });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  const events = data?.events?.slice(0, 8) || [];

  return (
    <div className="chrono-ribbon border-t border-[var(--border-glow)] bg-[rgba(5,7,10,0.98)] px-3 py-1.5">
      <div className="flex items-center gap-3">
        <div className="flex shrink-0 items-center gap-1 text-[9px] text-[var(--text-muted)]">
          <Clock className="h-3 w-3" />
          <span>CHRONO</span>
          <button onClick={rewind} className="ml-1 rounded bg-[rgba(0,242,255,0.1)] px-1.5 py-0.5 text-[var(--accent-cyan)] hover:bg-[rgba(0,242,255,0.2)]">
            <Rewind className="inline h-2.5 w-2.5" /> Rewind
          </button>
        </div>
        <div className="flex flex-1 gap-2 overflow-x-auto scrollbar-thin">
          {events.map((e, i) => (
            <div key={i} className="flex shrink-0 items-center gap-1 rounded bg-[rgba(0,0,0,0.3)] px-2 py-0.5 text-[8px]">
              <span className={cn("font-bold uppercase", DAPP_COLORS[e.dapp] || "text-white")}>{e.dapp}</span>
              <span className="text-[var(--text-muted)]">{e.label}</span>
            </div>
          ))}
          {events.length === 0 && <span className="text-[9px] text-[var(--text-muted)]">No timeline events yet — act across DApps to populate Chrono</span>}
        </div>
      </div>
    </div>
  );
}
