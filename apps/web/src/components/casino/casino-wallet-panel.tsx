"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";

export function CasinoWalletPanel() {
  const qc = useQueryClient();
  const { data: wallet } = useQuery({ queryKey: queryKeys.casinoWallet, queryFn: () => api.casino.wallet() });
  const { data: history } = useQuery({ queryKey: queryKeys.casinoHistory, queryFn: () => api.casino.history(), refetchInterval: 15000 });
  const [amount, setAmount] = useState("100");
  const [currency, setCurrency] = useState("MGANGA");

  const deposit = async () => {
    const val = parseFloat(amount);
    if (!val || val <= 0) return;
    await toastAction(() => api.casino.deposit(val, currency), {
      loading: "Depositing chips...",
      success: (r) => `Deposited ${(r as { deposited: number }).deposited} ${currency} chips`,
    });
    qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.defiWallet("TRD-8F7C-29D1") });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
      <GlassPanel title="Deposit Chips" variant="gold">
        <div className="space-y-2 text-sm">
          <div className="flex gap-2 text-[10px] text-[var(--text-muted)]">
            <span>MGANGA: {wallet?.mganga_chips?.toLocaleString() ?? 0}</span>
            <span>MWANJESA: {wallet?.mwanjesa_chips?.toLocaleString() ?? 0}</span>
          </div>
          <div className="flex gap-2">
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="input-field flex-1"
              placeholder="Amount"
            />
            <select value={currency} onChange={(e) => setCurrency(e.target.value)} className="input-field">
              <option value="MGANGA">MGANGA</option>
              <option value="MWANJESA">MWANJESA</option>
            </select>
          </div>
          <button onClick={deposit} className="btn-primary btn-cefi w-full">Deposit from Wallet</button>
          <p className="text-[10px] text-[var(--text-muted)]">
            Net: {(wallet?.net_profit ?? 0) >= 0 ? "+" : ""}{wallet?.net_profit?.toFixed(2)} · {wallet?.games_played ?? 0} games
          </p>
        </div>
      </GlassPanel>

      <GlassPanel title="Bet History" variant="violet">
        <div className="max-h-40 space-y-1 overflow-y-auto scrollbar-thin text-[10px]">
          {(history || []).length === 0 && (
            <p className="text-[var(--text-muted)]">No bets yet — pick a game above.</p>
          )}
          {(history || []).map((b) => (
            <div key={b.id} className="flex items-center justify-between rounded bg-[rgba(0,0,0,0.2)] px-2 py-1">
              <span className="capitalize">{b.game}</span>
              <span>{b.amount}</span>
              <span className={cn(b.won ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>
                {b.won ? `+${b.payout}` : `-${b.amount}`}
              </span>
              <span className="text-[var(--text-muted)]">{b.multiplier}x</span>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );
}
