"use client";

import { useOmniverseStore } from "@/store/omniverse";
import { cn } from "@/lib/utils";

export function OmniverseLayer({ children }: { children: React.ReactNode }) {
  const { dimension, overdrive } = useOmniverseStore();

  return (
    <div
      className={cn(
        "omniverse-layer min-h-full transition-all duration-700",
        `dim-${dimension}`,
        overdrive && "overdrive-active",
        dimension === 99 && "dim-infinite"
      )}
    >
      {overdrive && <div className="overdrive-scanlines pointer-events-none fixed inset-0 z-50" />}
      {dimension >= 5 && <div className="hyper-tunnel pointer-events-none fixed inset-0 z-0" />}
      <div className="relative z-10">{children}</div>
    </div>
  );
}
