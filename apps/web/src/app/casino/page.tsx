"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Dices, Trophy, Radio, Users } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { Hypercube4D } from "@/components/casino/hypercube-4d";
import { CASINO_GAMES } from "@/lib/casino-games";
import { api, queryKeys } from "@/lib/api";
import { cn } from "@/lib/utils";

export default function CasinoPage() {
  const { data: wallet, isLoading: wLoading } = useQuery({ queryKey: queryKeys.casinoWallet, queryFn: () => api.casino.wallet() });
  const { data: feed } = useQuery({ queryKey: queryKeys.casinoFeed, queryFn: () => api.casino.liveFeed(), refetchInterval: 5000 });
  const { data: board } = useQuery({ queryKey: queryKeys.casinoLeaderboard, queryFn: () => api.casino.leaderboard() });

  return (
    <div className="mx-auto max-w-6xl space-y-6 animate-fade-in">
      <div className="relative overflow-hidden rounded-2xl border border-[var(--border-glow)] bg-gradient-to-r from-[rgba(138,43,226,0.15)] via-[rgba(0,242,255,0.1)] to-[rgba(255,215,0,0.15)] p-6">
        <div className="absolute right-8 top-4 opacity-40">
          <Hypercube4D size={140} active />
        </div>
        <div className="relative z-10">
          <h1 className="text-3xl font-bold neon-text-violet">TessSocial Casino</h1>
          <p className="mt-1 text-sm text-[var(--text-muted)]">7 games · 3D & 4D immersive play · RF-SAM provably fair proofs</p>
          {wLoading ? <LoadingSpinner className="mt-4" /> : (
            <div className="mt-4 flex flex-wrap gap-4 text-sm">
              <span className="rounded-lg bg-[rgba(0,242,255,0.15)] px-3 py-1 font-mono text-[var(--accent-cyan)]">
                {wallet?.mganga_chips?.toLocaleString()} MGANGA chips
              </span>
              <span className="rounded-lg bg-[rgba(138,43,226,0.15)] px-3 py-1 font-mono text-[var(--accent-violet)]">
                {wallet?.mwanjesa_chips?.toLocaleString()} MWANJESA chips
              </span>
              <span className="text-[var(--accent-green)]">Streak: {wallet?.win_streak ?? 0} 🔥</span>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-4 gap-3">
        {CASINO_GAMES.map((g) => (
          <Link key={g.id} href={`/casino/${g.id}`}>
            <GlassPanel
              className={cn(
                "group h-full cursor-pointer transition-all duration-300 hover:scale-[1.02] hover:border-[var(--accent-cyan)] hover:shadow-[0_0_30px_rgba(0,242,255,0.2)]",
                `bg-gradient-to-br ${g.gradient}`
              )}
              variant={g.dimension === "4D" ? "gold" : "violet"}
            >
              <div className="flex items-start justify-between">
                <span className="text-3xl transition-transform group-hover:scale-125">{g.emoji}</span>
                <span className={cn("rounded px-1.5 py-0.5 text-[8px] font-bold", g.dimension === "4D" ? "bg-[var(--accent-gold)]/30 text-[var(--accent-gold)]" : "bg-[var(--accent-violet)]/30 text-[var(--accent-violet)]")}>
                  {g.dimension}
                </span>
              </div>
              <h3 className="mt-2 font-bold">{g.name}</h3>
              <p className="mt-1 text-[10px] text-[var(--text-muted)] line-clamp-2">{g.description}</p>
              <p className="mt-2 text-[10px] text-[var(--accent-green)]">Up to {g.max_multiplier}x · Play →</p>
            </GlassPanel>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-4">
        <GlassPanel title="Live Wins" action={<Radio className="h-3 w-3 animate-pulse text-[var(--accent-red)]" />}>
          <div className="max-h-48 space-y-2 overflow-y-auto scrollbar-thin text-[10px]">
            {(feed || []).map((f, i) => (
              <div key={i} className="flex justify-between rounded bg-[rgba(0,0,0,0.2)] px-2 py-1">
                <span>{f.player}</span>
                <span className="text-[var(--text-muted)]">{f.game}</span>
                <span className={f.won ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}>
                  {f.won ? `+${f.payout}` : `-${f.amount}`}
                </span>
              </div>
            ))}
          </div>
        </GlassPanel>

        <GlassPanel title="Leaderboard" variant="gold" action={<Trophy className="h-3 w-3 text-[var(--accent-gold)]" />}>
          <div className="space-y-2 text-[10px]">
            {(board || []).map((p) => (
              <div key={p.rank} className="flex justify-between">
                <span>#{p.rank} {p.player}</span>
                <span className="text-[var(--accent-gold)]">{p.total_won.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </GlassPanel>

        <GlassPanel title="RF-SAM Proof System" variant="violet">
          <div className="space-y-2 text-[10px] text-[var(--text-muted)]">
            <p><Users className="inline h-3 w-3" /> Social casino with on-chain-ready proofs</p>
            <p>Every bet uses HMAC-SHA256 seed attestation</p>
            <p>Server seed committed before play · Client seed + nonce</p>
            <p className="text-[var(--accent-cyan)]">Verify any bet instantly in-game</p>
          </div>
        </GlassPanel>
      </div>
    </div>
  );
}
