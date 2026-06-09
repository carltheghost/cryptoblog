"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { formatUsd } from "@/lib/utils";
import { usePlatformStore } from "@/store/platform";
import { toastAction } from "@/hooks/use-toast-action";

export function NonCustodialWallet() {
  const { tessId } = usePlatformStore();
  const { data: wallet, isLoading } = useQuery({
    queryKey: queryKeys.defiWallet(tessId),
    queryFn: () => api.defi.wallet(tessId),
  });

  if (isLoading) return <GlassPanel title="Non-Custodial Wallet" variant="violet"><LoadingSpinner className="py-4" /></GlassPanel>;
  const tokens = wallet?.tokens || [];

  return (
    <GlassPanel title="Non-Custodial Wallet" variant="violet" className="animate-fade-in">
      <p className="mb-2 font-mono text-2xl font-bold text-[var(--accent-violet)]">{formatUsd(wallet?.mwanjesa_balance ?? 0)}</p>
      <div className="space-y-1 text-xs">
        {tokens.map((t) => (
          <div key={t.symbol} className="flex justify-between">
            <span className="font-semibold">{t.symbol}</span>
            <span className="text-[var(--text-muted)]">{t.balance.toLocaleString()} · {formatUsd(t.usd_value)}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function DexSwap() {
  const [from, setFrom] = useState("ETH");
  const [to, setTo] = useState("USDC");
  const [amount, setAmount] = useState("1");
  const [quote, setQuote] = useState<{ output_amount: number; provider: string; price_impact: number } | null>(null);
  const [busy, setBusy] = useState(false);
  const qc = useQueryClient();
  const { tessId } = usePlatformStore();

  const getQuote = async () => {
    setBusy(true);
    try {
      const q = await api.defi.swapQuote({ from_token: from, to_token: to, amount: parseFloat(amount) });
      setQuote(q as typeof quote);
    } catch (e) {
      setQuote(null);
    }
    setBusy(false);
  };

  const execute = async () => {
    setBusy(true);
    const result = await toastAction(
      () => api.defi.swapExecute({ from_token: from, to_token: to, amount: parseFloat(amount) }),
      {
        loading: "Executing swap...",
        success: (r) => `Swapped! Received ${(r as { output_amount: number }).output_amount.toFixed(4)} ${to}`,
      }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: queryKeys.defiWallet(tessId) });
      qc.invalidateQueries({ queryKey: queryKeys.defiTx });
      setQuote(null);
    }
    setBusy(false);
  };

  return (
    <GlassPanel title="DEX Swap" variant="violet" className="animate-fade-in">
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <select value={from} onChange={(e) => setFrom(e.target.value)} className="input-field flex-1">
            {["ETH", "USDC", "TRD", "MWANJESA"].map((t) => <option key={t}>{t}</option>)}
          </select>
          <span className="text-[var(--text-muted)]">→</span>
          <select value={to} onChange={(e) => setTo(e.target.value)} className="input-field flex-1">
            {["USDC", "ETH", "TRD", "MWANJESA"].map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field" type="number" min="0" step="0.01" />
        {quote && (
          <div className="rounded-lg bg-[rgba(138,43,226,0.08)] p-2 text-[var(--text-muted)]">
            <p>Output: <span className="text-[var(--accent-violet)]">{quote.output_amount.toFixed(4)} {to}</span></p>
            <p className="text-[10px]">via {quote.provider} · impact {quote.price_impact}%</p>
          </div>
        )}
        <div className="flex gap-2">
          <button onClick={getQuote} disabled={busy} className="btn-primary flex-1 bg-[rgba(138,43,226,0.2)] text-[var(--accent-violet)]">Get Quote</button>
          <button onClick={execute} disabled={busy || !quote} className="btn-primary btn-defi flex-1">Swap Now</button>
        </div>
      </div>
    </GlassPanel>
  );
}
