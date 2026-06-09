"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Dices } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api, queryKeys } from "@/lib/api";
import { CASINO_GAMES } from "@/lib/casino-games";

export function CasinoWidget() {
  const { data: casino } = useQuery({ queryKey: queryKeys.casinoWallet, queryFn: () => api.casino.wallet() });
  const { data: feed } = useQuery({ queryKey: queryKeys.casinoFeed, queryFn: () => api.casino.liveFeed(), refetchInterval: 8000 });

  return (
    <GlassPanel title="TessSocial Casino" variant="gold" action={
      <Link href="/casino" className="flex items-center gap-1 text-[10px] text-[var(--accent-gold)] hover:underline">
        <Dices className="h-3 w-3" /> Play
      </Link>
    }>
      <div className="flex gap-3 text-[10px]">
        <span className="text-[var(--accent-cyan)]">{(casino?.mganga_chips ?? 0).toLocaleString()} chips</span>
        <span className="text-[var(--accent-green)]">🔥 {casino?.win_streak ?? 0}</span>
      </div>
      <div className="mt-2 flex gap-1">
        {CASINO_GAMES.slice(0, 4).map((g) => (
          <Link key={g.id} href={`/casino/${g.id}`} title={g.name} className="text-lg transition-transform hover:scale-125">
            {g.emoji}
          </Link>
        ))}
      </div>
      {(feed?.[0]) && (
        <p className="mt-2 text-[9px] text-[var(--text-muted)]">
          {feed[0].player} {feed[0].won ? "won" : "lost"} on {feed[0].game}
        </p>
      )}
    </GlassPanel>
  );
}
