"use client";

import { ModeToggle } from "./mode-toggle";
import { usePlatformStore } from "@/store/platform";

export function Header() {
  const { mode } = usePlatformStore();

  return (
    <header className="flex h-14 items-center justify-between border-b border-[var(--border-glow)] bg-[rgba(5,7,10,0.95)] px-4">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-full bg-gradient-to-br from-[var(--accent-cyan)] to-[var(--accent-violet)]" />
        <div>
          <p className="text-sm font-semibold">TraderOne Pro</p>
          <p className="text-[10px] text-[var(--text-muted)]">
            {mode === "centralized" ? "CeFi Power · Fiat On-Ramp · High Speed" : "DeFi Freedom · Non-Custodial · Web3 Native"}
          </p>
        </div>
      </div>
      <ModeToggle />
      <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
        <div className="h-2 w-2 rounded-full bg-[var(--accent-green)]" />
        All Systems Operational
      </div>
    </header>
  );
}
