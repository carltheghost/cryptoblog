"use client";

import { useState } from "react";
import Link from "next/link";
import { useQueryClient } from "@tanstack/react-query";
import { ArrowLeft, Zap } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { Hypercube4D } from "@/components/casino/hypercube-4d";
import { RfsamProof } from "@/components/casino/rfsam-proof";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";
import type { CasinoGame } from "@/lib/casino-games";

interface BetResult {
  bet_id: number;
  won: boolean;
  payout: number;
  multiplier: number;
  profit: number;
  outcome: Record<string, unknown>;
  proof: { algorithm: string; server_seed_hash: string; client_seed: string; nonce: number; digest: string; game: string };
  chips_remaining: number;
  win_streak: number;
}

export function GameShell({
  game,
  children,
  choice,
  choiceLabel,
  extraControls,
}: {
  game: CasinoGame;
  children: React.ReactNode | ((state: { result: BetResult | null; playing: boolean }) => React.ReactNode);
  choice: string;
  choiceLabel?: string;
  extraControls?: React.ReactNode;
}) {
  const qc = useQueryClient();
  const [amount, setAmount] = useState(String(game.min_bet));
  const [currency, setCurrency] = useState<"MGANGA" | "MWANJESA">("MGANGA");
  const [playing, setPlaying] = useState(false);
  const [result, setResult] = useState<BetResult | null>(null);

  const play = async () => {
    setPlaying(true);
    setResult(null);
    const res = await toastAction(
      () => api.casino.bet({ game: game.id, amount: parseFloat(amount), currency, choice }),
      {
        loading: "Rolling RF-SAM outcome...",
        success: (r) => {
          const bet = r as unknown as BetResult;
          return bet.won ? `Won ${bet.payout} chips! (${bet.multiplier}x)` : `Lost ${amount} chips`;
        },
      }
    );
    if (res) {
      setResult(res as BetResult);
      qc.invalidateQueries({ queryKey: queryKeys.casinoWallet });
      qc.invalidateQueries({ queryKey: queryKeys.casinoHistory });
      qc.invalidateQueries({ queryKey: queryKeys.casinoFeed });
    }
    setPlaying(false);
  };

  const childContent = typeof children === "function" ? children({ result, playing }) : children;

  return (
    <div className="mx-auto max-w-4xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <Link href="/casino" className="flex items-center gap-2 text-xs text-[var(--text-muted)] hover:text-[var(--accent-cyan)]">
          <ArrowLeft className="h-4 w-4" /> Casino Lobby
        </Link>
        <span className={cn("rounded-full px-2 py-0.5 text-[10px] font-bold", game.dimension === "4D" ? "bg-[var(--accent-gold)]/20 text-[var(--accent-gold)]" : "bg-[var(--accent-violet)]/20 text-[var(--accent-violet)]")}>
          {game.dimension} VIEW
        </span>
      </div>

      <div className="flex items-center gap-4">
        <Hypercube4D size={64} active={playing} />
        <div>
          <h1 className="text-2xl font-bold neon-text-cyan">{game.emoji} {game.name}</h1>
          <p className="text-xs text-[var(--text-muted)]">{game.description} · Max {game.max_multiplier}x</p>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <GlassPanel className="col-span-2 min-h-[280px] flex items-center justify-center overflow-hidden" variant={game.dimension === "4D" ? "gold" : "violet"}>
          <div className={cn("w-full transition-all", playing && "game-playing-pulse")}>
            {childContent}
          </div>
        </GlassPanel>

        <div className="space-y-3">
          <GlassPanel title="Place Bet">
            <div className="space-y-2 text-xs">
              {choiceLabel && <p className="text-[var(--text-muted)]">{choiceLabel}: <span className="text-[var(--accent-cyan)]">{choice}</span></p>}
              <select value={currency} onChange={(e) => setCurrency(e.target.value as "MGANGA" | "MWANJESA")} className="input-field">
                <option value="MGANGA">MGANGA Chips</option>
                <option value="MWANJESA">MWANJESA Chips</option>
              </select>
              <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field" type="number" min={game.min_bet} />
              {extraControls}
              <button onClick={play} disabled={playing} className="btn-primary btn-defi w-full flex items-center justify-center gap-2">
                <Zap className="h-4 w-4" /> {playing ? "Playing..." : "Play Now"}
              </button>
            </div>
          </GlassPanel>

          {result && (
            <GlassPanel variant={result.won ? "green" : "default"}>
              <p className={cn("text-sm font-bold", result.won ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>
                {result.won ? "WIN" : "LOSS"} · {result.multiplier}x
              </p>
              <p className="text-xs text-[var(--text-muted)]">Payout: {result.payout} · Streak: {result.win_streak}</p>
            </GlassPanel>
          )}

          {result?.proof && <RfsamProof proof={result.proof} betId={result.bet_id} />}
          <UnthinkablePanel dapp="casino" action={`game-${game.id}`} compact />
        </div>
      </div>
    </div>
  );
}
