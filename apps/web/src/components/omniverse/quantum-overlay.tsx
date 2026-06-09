"use client";

import { useQuery } from "@tanstack/react-query";
import { Eye } from "lucide-react";
import { api, queryKeys } from "@/lib/api";
import { useOmniverseStore } from "@/store/omniverse";
import { cn } from "@/lib/utils";

export function QuantumBalance({
  realm,
  value,
  className,
}: {
  realm: "cefi" | "defi" | "casino";
  value: number;
  className?: string;
}) {
  const quantumSuperposed = useOmniverseStore((s) => s.quantumSuperposed);
  const { data } = useQuery({
    queryKey: queryKeys.quantumState,
    queryFn: () => api.omniverse.quantum(),
    enabled: quantumSuperposed,
    staleTime: 10_000,
  });

  const state = data?.states?.find((s) => s.realm === realm);

  if (!quantumSuperposed || !state) {
    return <span className={cn("font-mono", className)}>{value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>;
  }

  return (
    <span className={cn("relative inline-block font-mono quantum-state-bar", className)}>
      <span className="text-[var(--accent-violet)]">{value.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
      <span className="ml-1 text-[8px] text-[var(--text-muted)]">
        Ψ[{state.alt_low}–{state.alt_high}]
      </span>
      <Eye className="ml-0.5 inline h-2.5 w-2.5 text-[var(--accent-violet)] opacity-60" />
    </span>
  );
}
