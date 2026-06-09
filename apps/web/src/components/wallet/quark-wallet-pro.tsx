"use client";

import Link from "next/link";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Dices, Wallet, Zap, Shield, Gamepad2 } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Hypercube4D } from "@/components/casino/hypercube-4d";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { formatUsd } from "@/lib/utils";
import { usePlatformStore } from "@/store/platform";
import { CASINO_GAMES } from "@/lib/casino-games";

export function QuarkWalletPro() {
  const { tessId } = usePlatformStore();
  const qc = useQueryClient();
  const { data: hybrid } = useQuery({ queryKey: queryKeys.hybridBalances, queryFn: () => api.identity.hybridBalances() });
  const { data: casino } = useQuery({ queryKey: queryKeys.casinoWallet, queryFn: () => api.casino.wallet() });
  const { data: defi } = useQuery({ queryKey: queryKeys.defiWallet(tessId), queryFn: () => api.defi.wallet(tessId) });

  const depositChips = async (amount: number, currency: string) => {
    await toastAction(() => api.casino.deposit(amount, currency), {
      success: `Deposited ${amount} ${currency} to casino chips`,
    });
    qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    qc.invalidateQueries({ queryKey: queryKeys.defiWallet(tessId) });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
  };

  const totalChips = (casino?.mganga_chips ?? 0) + (casino?.mwanjesa_chips ?? 0);
  const totalBalance = (hybrid?.cefi_balance ?? 0) + (hybrid?.defi_balance ?? 0);

  return (
    <GlassPanel className="relative overflow-hidden" variant="gold">
      <div className="absolute -right-6 -top-6 opacity-30">
        <Hypercube4D size={160} active />
      </div>

      <div className="relative z-10">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Wallet className="h-5 w-5 text-[var(--accent-gold)]" />
            <h2 className="text-lg font-bold neon-text-gold">Quark Wallet Pro</h2>
          </div>
          <span className="rounded-full bg-[var(--accent-green)]/20 px-2 py-0.5 text-[10px] text-[var(--accent-green)]">4D ENABLED</span>
        </div>

        <p className="mt-1 font-mono text-[10px] text-[var(--accent-cyan)]">{hybrid?.tess_id ?? tessId}</p>

        <div className="mt-4 grid grid-cols-3 gap-3">
          <div className="rounded-lg bg-[rgba(0,242,255,0.08)] p-3 text-center">
            <p className="text-[10px] text-[var(--text-muted)]">Total Portfolio</p>
            <p className="font-mono text-lg font-bold text-[var(--accent-cyan)]">{formatUsd(totalBalance)}</p>
          </div>
          <div className="rounded-lg bg-[rgba(138,43,226,0.08)] p-3 text-center">
            <p className="text-[10px] text-[var(--text-muted)]">Casino Chips</p>
            <p className="font-mono text-lg font-bold text-[var(--accent-violet)]">{totalChips.toLocaleString()}</p>
          </div>
          <div className="rounded-lg bg-[rgba(255,215,0,0.08)] p-3 text-center">
            <p className="text-[10px] text-[var(--text-muted)]">Casino P/L</p>
            <p className={`font-mono text-lg font-bold ${(casino?.net_profit ?? 0) >= 0 ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}`}>
              {(casino?.net_profit ?? 0) >= 0 ? "+" : ""}{casino?.net_profit ?? 0}
            </p>
          </div>
        </div>

        <div className="mt-4 flex flex-wrap gap-2">
          <button onClick={() => depositChips(500, "MGANGA")} className="btn-primary btn-cefi flex items-center gap-1 text-[10px]">
            <Zap className="h-3 w-3" /> +500 MGANGA → Chips
          </button>
          <button onClick={() => depositChips(300, "MWANJESA")} className="btn-primary btn-defi flex items-center gap-1 text-[10px]">
            <Zap className="h-3 w-3" /> +300 MWANJESA → Chips
          </button>
          <Link href="/casino" className="btn-primary flex items-center gap-1 bg-[rgba(255,215,0,0.2)] text-[var(--accent-gold)] text-[10px]">
            <Dices className="h-3 w-3" /> Play Casino
          </Link>
        </div>

        <div className="mt-4">
          <p className="mb-2 text-[10px] uppercase tracking-wider text-[var(--text-muted)]">Quick Play — 3D & 4D Games</p>
          <div className="flex gap-2 overflow-x-auto pb-1 scrollbar-thin">
            {CASINO_GAMES.slice(0, 5).map((g) => (
              <Link
                key={g.id}
                href={`/casino/${g.id}`}
                className="flex shrink-0 flex-col items-center rounded-lg border border-[var(--border-glow)] bg-[rgba(0,0,0,0.3)] px-3 py-2 transition-all hover:border-[var(--accent-cyan)] hover:bg-[rgba(0,242,255,0.1)]"
              >
                <span className="text-xl">{g.emoji}</span>
                <span className="mt-1 text-[9px] font-semibold">{g.name.split(" ")[0]}</span>
                <span className="text-[8px] text-[var(--accent-violet)]">{g.dimension}</span>
              </Link>
            ))}
            <Link href="/casino" className="flex shrink-0 items-center rounded-lg border border-dashed border-[var(--text-muted)] px-3 text-[10px] text-[var(--text-muted)] hover:text-[var(--accent-cyan)]">
              <Gamepad2 className="h-4 w-4" /> All 7
            </Link>
          </div>
        </div>

        <div className="mt-3 grid grid-cols-4 gap-2 text-[9px] text-[var(--text-muted)]">
          <div className="flex items-center gap-1"><Shield className="h-3 w-3 text-[var(--accent-green)]" /> RF-SAM</div>
          <div>Games: {casino?.games_played ?? 0}</div>
          <div>Streak: {casino?.win_streak ?? 0}🔥</div>
          <div>Staked: {(defi?.staked_trd ?? 0).toLocaleString()}</div>
        </div>
      </div>
    </GlassPanel>
  );
}
