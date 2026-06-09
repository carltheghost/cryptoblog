"use client";

import { use } from "react";
import { CasinoGameView } from "@/components/casino/games";

export default function CasinoGamePage({ params }: { params: Promise<{ game: string }> }) {
  const { game } = use(params);
  return <CasinoGameView gameId={game} />;
}
