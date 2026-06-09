"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { formatUsd } from "@/lib/utils";
import { usePlatformStore } from "@/store/platform";

export function NonCustodialWallet() {
  const { tessId } = usePlatformStore();
  const [wallet, setWallet] = useState({ mwanjesa_balance: 0, tokens: [] as { symbol: string; balance: number; usd_value: number }[] });

  useEffect(() => { api.defi.wallet(tessId).then(setWallet); }, [tessId]);

  return (
    <GlassPanel title="Non-Custodial Wallet" variant="violet">
      <p className="mb-2 font-mono text-2xl font-bold text-[var(--accent-violet)]">{formatUsd(wallet.mwanjesa_balance)}</p>
      <div className="space-y-1 text-xs">
        {wallet.tokens?.map((t) => (
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
  const [quote, setQuote] = useState<{ output_amount: number; route: string[]; provider: string } | null>(null);

  const getQuote = async () => {
    const q = await api.defi.swapQuote({ from_token: from, to_token: to, amount: parseFloat(amount) });
    setQuote(q as typeof quote);
  };

  const execute = async () => {
    await api.defi.swapExecute({ from_token: from, to_token: to, amount: parseFloat(amount) });
    alert("Swap executed!");
  };

  return (
    <GlassPanel title="DEX Swap" variant="violet">
      <div className="space-y-2 text-xs">
        <div className="flex gap-2">
          <select value={from} onChange={(e) => setFrom(e.target.value)} className="flex-1 rounded-lg bg-[rgba(0,0,0,0.3)] px-2 py-2 text-white border border-[rgba(138,43,226,0.3)]">
            {["ETH", "USDC", "TRD", "MWANJESA"].map((t) => <option key={t}>{t}</option>)}
          </select>
          <span className="self-center text-[var(--text-muted)]">→</span>
          <select value={to} onChange={(e) => setTo(e.target.value)} className="flex-1 rounded-lg bg-[rgba(0,0,0,0.3)] px-2 py-2 text-white border border-[rgba(138,43,226,0.3)]">
            {["USDC", "ETH", "TRD", "MWANJESA"].map((t) => <option key={t}>{t}</option>)}
          </select>
        </div>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]" />
        {quote && (
          <p className="text-[var(--text-muted)]">
            Output: <span className="text-[var(--accent-violet)]">{quote.output_amount.toFixed(4)} {to}</span> via {quote.provider}
          </p>
        )}
        <div className="flex gap-2">
          <button onClick={getQuote} className="flex-1 rounded-lg bg-[rgba(138,43,226,0.2)] py-2 text-[var(--accent-violet)]">Get Quote</button>
          <button onClick={execute} className="flex-1 rounded-lg bg-[var(--accent-violet)] py-2 font-bold text-white">Swap Now</button>
        </div>
      </div>
    </GlassPanel>
  );
}
