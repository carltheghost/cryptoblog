"use client";

import { usePlatformStore } from "@/store/platform";
import { cn } from "@/lib/utils";

export function ModeToggle() {
  const { mode, setMode } = usePlatformStore();

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => setMode("centralized")}
        className={cn(
          "rounded-full px-5 py-2 text-xs font-bold uppercase tracking-wider transition-all",
          mode === "centralized"
            ? "bg-[rgba(0,242,255,0.2)] text-[var(--accent-cyan)] shadow-[0_0_20px_rgba(0,242,255,0.3)]"
            : "text-[var(--text-muted)] hover:text-[var(--accent-cyan)]"
        )}
      >
        Centralized Mode
      </button>
      <div className="relative h-6 w-12 cursor-pointer rounded-full bg-[rgba(255,255,255,0.1)]" onClick={() => setMode(mode === "centralized" ? "decentralized" : "centralized")}>
        <div
          className={cn(
            "absolute top-0.5 h-5 w-5 rounded-full transition-all duration-300",
            mode === "centralized" ? "left-0.5 bg-[var(--accent-cyan)]" : "left-6 bg-[var(--accent-violet)]"
          )}
        />
      </div>
      <button
        onClick={() => setMode("decentralized")}
        className={cn(
          "rounded-full px-5 py-2 text-xs font-bold uppercase tracking-wider transition-all",
          mode === "decentralized"
            ? "bg-[rgba(138,43,226,0.2)] text-[var(--accent-violet)] shadow-[0_0_20px_rgba(138,43,226,0.3)]"
            : "text-[var(--text-muted)] hover:text-[var(--accent-violet)]"
        )}
      >
        Decentralized Mode
      </button>
    </div>
  );
}
