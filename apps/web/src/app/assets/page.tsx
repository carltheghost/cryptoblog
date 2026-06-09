"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { formatUsd } from "@/lib/utils";

export default function AssetsPage() {
  const [cefi, setCefi] = useState({ mganga_balance: 0 });
  const [defi, setDefi] = useState({ mwanjesa_balance: 0, staked_trd: 0 });

  useEffect(() => {
    api.cefi.account().then(setCefi);
    api.defi.wallet("TRD-8F7C-29D1").then(setDefi);
  }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Assets</h1>
      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="CeFi Assets (MGANGA)">
          <p className="font-mono text-2xl font-bold text-[var(--accent-cyan)]">{formatUsd(cefi.mganga_balance)}</p>
        </GlassPanel>
        <GlassPanel title="DeFi Assets (MWANJESA)" variant="violet">
          <p className="font-mono text-2xl font-bold text-[var(--accent-violet)]">{formatUsd(defi.mwanjesa_balance)}</p>
          <p className="text-xs text-[var(--text-muted)]">Staked: {defi.staked_trd?.toLocaleString()} TRD</p>
        </GlassPanel>
      </div>
    </div>
  );
}
