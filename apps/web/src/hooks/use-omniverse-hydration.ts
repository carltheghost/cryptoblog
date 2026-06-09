"use client";

import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";
import { api, queryKeys } from "@/lib/api";
import { useOmniverseStore, type Dimension } from "@/store/omniverse";

export function useOmniverseHydration() {
  const hydrate = useOmniverseStore((s) => s.hydrate);
  const { data } = useQuery({
    queryKey: queryKeys.omniverseStatus,
    queryFn: () => api.omniverse.status(),
    staleTime: 30_000,
  });

  useEffect(() => {
    if (!data) return;
    hydrate({
      dimension: data.dimension as Dimension,
      overdrive: data.overdrive,
      quantumSuperposed: data.quantum_locked,
      impossibilityIndex: data.impossibility_index,
      paradoxCount: data.paradox_count,
      realityStability: data.reality_stability,
    });
  }, [data, hydrate]);
}
