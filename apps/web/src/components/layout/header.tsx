"use client";

import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ModeToggle } from "./mode-toggle";
import { DimensionShift, TessOverdrive, QuantumToggle } from "@/components/omniverse/omniverse-controls";
import { usePlatformStore } from "@/store/platform";
import { api, queryKeys } from "@/lib/api";

export function Header() {
  const { mode } = usePlatformStore();
  const { data: health } = useQuery({
    queryKey: queryKeys.health,
    queryFn: () => api.health(),
    refetchInterval: 30000,
    retry: 1,
  });

  const online = health?.status === "ok";

  return (
    <header className="flex h-14 items-center justify-between border-b border-[var(--border-glow)] bg-[rgba(5,7,10,0.95)] px-4">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[var(--accent-cyan)] to-[var(--accent-violet)] shadow-[0_0_15px_rgba(0,242,255,0.3)]" />
        <div>
          <p className="text-sm font-semibold">TraderOne Pro</p>
          <p className="text-[10px] text-[var(--text-muted)]">
            {mode === "centralized" ? "CeFi Power · Fiat On-Ramp · High Speed" : "DeFi Freedom · Non-Custodial · Web3 Native"}
          </p>
        </div>
      </div>
      <div className="flex items-center gap-2">
        <DimensionShift />
        <QuantumToggle />
        <TessOverdrive />
        <Link href="/omniverse" className="rounded border border-[var(--accent-gold)] px-2 py-1 text-[9px] font-black text-[var(--accent-gold)] hover:bg-[rgba(255,215,0,0.1)]">
          ◈ OMNI
        </Link>
      </div>
      <ModeToggle />
      <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
        <div className={`h-2 w-2 rounded-full ${online ? "bg-[var(--accent-green)] pulse-glow" : "bg-[var(--accent-red)]"}`} />
        {online ? "All Systems Operational" : "Degraded Performance"}
      </div>
    </header>
  );
}
