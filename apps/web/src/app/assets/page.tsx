"use client";

import { useQuery } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { formatUsd } from "@/lib/utils";
import { usePlatformStore } from "@/store/platform";

export default function AssetsPage() {
  const { tessId } = usePlatformStore();
  const { data: cefi, isLoading: cLoading } = useQuery({ queryKey: queryKeys.cefiAccount, queryFn: () => api.cefi.account() });
  const { data: defi, isLoading: dLoading } = useQuery({ queryKey: queryKeys.defiWallet(tessId), queryFn: () => api.defi.wallet(tessId) });
  const { data: custody } = useQuery({ queryKey: queryKeys.cefiCustody, queryFn: () => api.cefi.custody() });
  const { data: hybrid } = useQuery({ queryKey: queryKeys.hybridBalances, queryFn: () => api.identity.hybridBalances() });

  if (cLoading || dLoading) return <LoadingSpinner />;

  const tokens = defi?.tokens || [];
  const allocations = custody?.allocations || [];
  const total = (hybrid?.cefi_balance ?? 0) + (hybrid?.defi_balance ?? 0);

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <h1 className="text-xl font-bold neon-text-cyan">Assets</h1>

      <GlassPanel title="Total Portfolio Value" variant="gold">
        <p className="font-mono text-3xl font-bold text-[var(--accent-gold)]">{formatUsd(total)}</p>
        <p className="text-xs text-[var(--text-muted)]">HYB Balance: {(hybrid?.hyb_balance ?? 0).toLocaleString()} HYB</p>
      </GlassPanel>

      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="CeFi Assets (MGANGA)">
          <p className="font-mono text-2xl font-bold text-[var(--accent-cyan)]">{formatUsd(cefi?.mganga_balance ?? 0)}</p>
          <p className="mt-2 text-xs text-[var(--text-muted)]">KYC: {cefi?.kyc_status}</p>
        </GlassPanel>
        <GlassPanel title="DeFi Assets (MWANJESA)" variant="violet">
          <p className="font-mono text-2xl font-bold text-[var(--accent-violet)]">{formatUsd(defi?.mwanjesa_balance ?? 0)}</p>
          <p className="mt-2 text-xs text-[var(--text-muted)]">Staked: {(defi?.staked_trd ?? 0).toLocaleString()} TRD</p>
        </GlassPanel>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <GlassPanel title="DeFi Token Breakdown" variant="violet">
          <div className="space-y-2 text-xs">
            {tokens.map((t) => (
              <div key={t.symbol} className="flex justify-between">
                <span className="font-semibold">{t.symbol}</span>
                <span>{t.balance.toLocaleString()} · {formatUsd(t.usd_value)}</span>
              </div>
            ))}
          </div>
        </GlassPanel>
        <GlassPanel title="Custody Vault">
          <div className="space-y-2 text-xs">
            {allocations.map((a) => (
              <div key={a.asset} className="flex justify-between">
                <span className="font-semibold">{a.asset}</span>
                <span className="text-[var(--text-muted)]">{a.amount.toLocaleString()} ({a.storage})</span>
              </div>
            ))}
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
