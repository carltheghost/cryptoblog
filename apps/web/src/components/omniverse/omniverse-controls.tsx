"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Infinity, Zap, Eye, Layers } from "lucide-react";
import { api, queryKeys } from "@/lib/api";
import { useOmniverseStore, DIMENSION_LABELS, type Dimension } from "@/store/omniverse";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";

const DIMS: Dimension[] = [1, 2, 3, 4, 5, 99];

export function DimensionShift() {
  const qc = useQueryClient();
  const { dimension, setDimension } = useOmniverseStore();

  const shift = async (d: Dimension) => {
    setDimension(d);
    await api.omniverse.setDimension(d);
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  return (
    <div className="flex items-center gap-1 rounded-lg border border-[var(--border-glow)] bg-[rgba(0,0,0,0.4)] p-1">
      <Layers className="ml-1 h-3 w-3 text-[var(--text-muted)]" />
      {DIMS.map((d) => (
        <button
          key={d}
          onClick={() => shift(d)}
          className={cn(
            "rounded px-1.5 py-0.5 text-[9px] font-bold transition-all",
            dimension === d
              ? d === 99
                ? "bg-gradient-to-r from-[var(--accent-gold)] to-[var(--accent-violet)] text-black"
                : "bg-[var(--accent-cyan)] text-black"
              : "text-[var(--text-muted)] hover:text-white"
          )}
        >
          {d === 99 ? <Infinity className="h-3 w-3" /> : `${d}D`}
        </button>
      ))}
    </div>
  );
}

export function TessOverdrive() {
  const qc = useQueryClient();
  const { overdrive, setOverdrive } = useOmniverseStore();
  const { data } = useQuery({ queryKey: queryKeys.omniverseStatus, queryFn: () => api.omniverse.status() });

  const toggle = async () => {
    const res = await toastAction(() => api.omniverse.overdrive(), {
      success: (r) => (r as { message: string }).message,
    });
    if (res) {
      setOverdrive((res as { overdrive: boolean }).overdrive);
      qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
    }
  };

  const active = overdrive || data?.overdrive;

  return (
    <button
      onClick={toggle}
      className={cn(
        "flex items-center gap-1 rounded-lg px-3 py-1.5 text-[10px] font-black transition-all",
        active
          ? "overdrive-btn animate-pulse bg-gradient-to-r from-[var(--accent-red)] via-[var(--accent-gold)] to-[var(--accent-violet)] text-black shadow-[0_0_20px_rgba(255,215,0,0.5)]"
          : "border border-[var(--accent-gold)] text-[var(--accent-gold)] hover:bg-[rgba(255,215,0,0.1)]"
      )}
    >
      <Zap className="h-3 w-3" />
      {active ? "OVERDRIVE" : "OVERDRIVE"}
    </button>
  );
}

export function QuantumToggle() {
  const qc = useQueryClient();
  const { quantumSuperposed, setQuantum } = useOmniverseStore();

  const toggle = async () => {
    if (quantumSuperposed) {
      await toastAction(() => api.omniverse.collapse("hybrid"), { success: "Wave function collapsed — hybrid realm observed" });
      setQuantum(false);
    } else {
      await toastAction(() => api.omniverse.entangle(), { success: "All balances entangled in superposition" });
      setQuantum(true);
    }
    qc.invalidateQueries({ queryKey: queryKeys.quantumState });
    qc.invalidateQueries({ queryKey: queryKeys.omniverseStatus });
  };

  return (
    <button onClick={toggle} className="flex items-center gap-1 rounded-lg border border-[var(--accent-violet)] px-2 py-1 text-[9px] text-[var(--accent-violet)] hover:bg-[rgba(138,43,226,0.15)]">
      <Eye className="h-3 w-3" />
      {quantumSuperposed ? "Collapse Ψ" : "Entangle Ψ"}
    </button>
  );
}
