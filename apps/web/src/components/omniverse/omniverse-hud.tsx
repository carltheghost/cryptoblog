"use client";

import { useOmniverseStore, DIMENSION_LABELS } from "@/store/omniverse";
import { cn } from "@/lib/utils";

export function OmniverseHud() {
  const { dimension, impossibilityIndex, paradoxCount, realityStability, overdrive } = useOmniverseStore();

  return (
    <div className="hidden items-center gap-2 rounded-lg border border-[var(--border-glow)] bg-[rgba(0,0,0,0.5)] px-2 py-1 md:flex">
      <div className="text-center">
        <p className="text-[7px] uppercase text-[var(--text-muted)]">Ω Index</p>
        <p className={cn("font-mono text-[10px] font-black", impossibilityIndex > 80 ? "text-[var(--accent-gold)]" : "text-[var(--accent-cyan)]")}>
          {impossibilityIndex.toFixed(1)}
        </p>
      </div>
      <div className="h-6 w-px bg-[var(--border-glow)]" />
      <div className="text-center">
        <p className="text-[7px] uppercase text-[var(--text-muted)]">Stability</p>
        <p className={cn("font-mono text-[10px] font-bold", realityStability < 70 ? "text-[var(--accent-red)]" : "text-[var(--accent-green)]")}>
          {realityStability}%
        </p>
      </div>
      <div className="h-6 w-px bg-[var(--border-glow)]" />
      <div className="text-center">
        <p className="text-[7px] uppercase text-[var(--text-muted)]">Paradox</p>
        <p className="font-mono text-[10px] font-bold text-[var(--accent-red)]">{paradoxCount}</p>
      </div>
      <div className="h-6 w-px bg-[var(--border-glow)]" />
      <div className="text-center">
        <p className="text-[7px] uppercase text-[var(--text-muted)]">View</p>
        <p className={cn("text-[9px] font-bold", overdrive ? "text-[var(--accent-gold)]" : "text-[var(--accent-violet)]")}>
          {DIMENSION_LABELS[dimension]}
        </p>
      </div>
    </div>
  );
}
