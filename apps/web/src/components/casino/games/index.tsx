"use client";

import { useState } from "react";
import { GameShell } from "@/components/casino/game-shell";
import { Dice3D, SlotReel3D, RouletteWheel3D, CrashRocket4D, Hypercube4D } from "@/components/casino/hypercube-4d";
import { getGame } from "@/lib/casino-games";
import { cn } from "@/lib/utils";

const WHEEL_COLORS = ["#ff4466", "#00ff88", "#ffd700", "#8a2be2", "#00f2ff", "#ff8800", "#ff4466", "#00ff88", "#ffd700", "#8a2be2", "#00f2ff", "#ff8800"];

function TessSlotsGame() {
  const game = getGame("tess-slots")!;
  return (
    <GameShell game={game} choice="spin">
      {({ result, playing }) => {
        const reels = (result?.outcome?.reels as string[]) || ["?", "?", "?"];
        return (
          <div className="flex items-center justify-center gap-4 py-8">
            {reels.map((s, i) => (
              <SlotReel3D key={i} symbol={s} spinning={playing} />
            ))}
          </div>
        );
      }}
    </GameShell>
  );
}

function HyperDiceGame() {
  const game = getGame("hyper-dice")!;
  const [target, setTarget] = useState("7");
  return (
    <GameShell game={game} choice={target} choiceLabel="Target sum" extraControls={
      <select value={target} onChange={(e) => setTarget(e.target.value)} className="input-field">
        {[2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12].map((n) => <option key={n} value={String(n)}>Sum = {n}</option>)}
      </select>
    }>
      {({ result, playing }) => {
        const dice = (result?.outcome?.dice as number[]) || [1, 1];
        return (
          <div className="flex items-center justify-center gap-8 py-8">
            <Dice3D value={dice[0] || 1} rolling={playing} />
            <span className="text-2xl font-bold text-[var(--accent-gold)]">+</span>
            <Dice3D value={dice[1] || 1} rolling={playing} />
            {result && <p className="absolute bottom-4 text-sm text-[var(--accent-cyan)]">Total: {result.outcome.total as number}</p>}
          </div>
        );
      }}
    </GameShell>
  );
}

function QuantumRouletteGame() {
  const game = getGame("quantum-roulette")!;
  const [pick, setPick] = useState("red");
  return (
    <GameShell game={game} choice={pick} choiceLabel="Bet on" extraControls={
      <select value={pick} onChange={(e) => setPick(e.target.value)} className="input-field">
        <option value="red">Red</option><option value="black">Black</option><option value="0">Green 0</option>
        {Array.from({ length: 37 }, (_, i) => <option key={i} value={String(i)}>Number {i}</option>)}
      </select>
    }>
      {({ result, playing }) => (
        <div className="relative flex flex-col items-center py-4">
          <RouletteWheel3D number={result?.outcome?.number as number} spinning={playing} />
          {result && <p className="mt-4 text-sm capitalize text-[var(--accent-green)]">Landed: {result.outcome.number as number} ({result.outcome.color as string})</p>}
        </div>
      )}
    </GameShell>
  );
}

function CrashOrbitGame() {
  const game = getGame("crash-orbit")!;
  const [cashout, setCashout] = useState("2.0");
  return (
    <GameShell game={game} choice={cashout} choiceLabel="Cash out at" extraControls={
      <input value={cashout} onChange={(e) => setCashout(e.target.value)} className="input-field" type="number" step="0.1" min="1.1" placeholder="Multiplier" />
    }>
      {({ result, playing }) => {
        const crash = (result?.outcome?.crash_point as number) || 1.0;
        const cashed = parseFloat(cashout);
        const crashed = result ? !result.won : false;
        const display = playing ? 1 + Math.random() * 3 : result ? (crashed ? crash : cashed) : 1.0;
        return <CrashRocket4D multiplier={display} crashed={crashed && !!result} />;
      }}
    </GameShell>
  );
}

function SoulWheelGame() {
  const game = getGame("soul-wheel")!;
  return (
    <GameShell game={game} choice="spin">
      {({ result, playing }) => {
        const seg = (result?.outcome?.segment as number) ?? 0;
        const mult = (result?.outcome?.label as string) || "?";
        return (
          <div className={cn("soul-wheel-scene", playing && "soul-wheel-spinning")}>
            <div className="soul-wheel" style={{ transform: result ? `rotate(${seg * 30}deg)` : undefined }}>
              {WHEEL_COLORS.map((c, i) => (
                <div key={i} className="soul-wheel-segment" style={{ transform: `rotate(${i * 30}deg)`, background: c }} />
              ))}
            </div>
            <div className="soul-wheel-pointer">▼</div>
            {result && <p className="mt-4 text-xl font-bold text-[var(--accent-gold)]">{mult}</p>}
          </div>
        );
      }}
    </GameShell>
  );
}

function TessPokerGame() {
  const game = getGame("tess-poker")!;
  return (
    <GameShell game={game} choice="high">
      {({ result, playing }) => {
        const player = (result?.outcome?.player as number) ?? 0;
        const dealer = (result?.outcome?.dealer as number) ?? 0;
        const rank = (n: number) => ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"][Math.min(n - 2, 12)] || "?";
        return (
          <div className="flex items-center justify-center gap-12 py-8">
            <div className={cn("poker-card-3d", playing && "poker-deal")}>
              <span className="text-3xl">🂡</span>
              <p className="text-xs">You: {rank(player)}</p>
            </div>
            <span className="text-[var(--text-muted)]">VS</span>
            <div className={cn("poker-card-3d poker-card-house", playing && "poker-deal")}>
              <span className="text-3xl">🂮</span>
              <p className="text-xs">House: {rank(dealer)}</p>
            </div>
          </div>
        );
      }}
    </GameShell>
  );
}

function HyperLotteryGame() {
  const game = getGame("hyper-lottery")!;
  const [pick, setPick] = useState("0000");
  return (
    <GameShell game={game} choice={pick} choiceLabel="Your 4D pick" extraControls={
      <input value={pick} onChange={(e) => setPick(e.target.value.replace(/\D/g, "").slice(0, 4).padStart(4, "0"))} className="input-field font-mono text-center text-lg tracking-[0.5em]" maxLength={4} />
    }>
      {({ result, playing }) => {
        const drawn = (result?.outcome?.drawn as number[]) || [0, 0, 0, 0];
        const matches = result?.outcome?.matches as number;
        return (
          <div className="flex flex-col items-center gap-6 py-6">
            <Hypercube4D size={100} active={playing || !!result} />
            <div className="flex gap-3">
              {drawn.map((d, i) => (
                <div key={i} className={cn("lottery-digit-4d", playing && "lottery-digit-spin")}>
                  {playing ? "?" : d}
                </div>
              ))}
            </div>
            {result && <p className="text-sm text-[var(--accent-cyan)]">{matches} digit(s) matched · {result.multiplier}x</p>}
          </div>
        );
      }}
    </GameShell>
  );
}

const GAME_MAP: Record<string, () => React.ReactElement> = {
  "tess-slots": TessSlotsGame,
  "hyper-dice": HyperDiceGame,
  "quantum-roulette": QuantumRouletteGame,
  "crash-orbit": CrashOrbitGame,
  "soul-wheel": SoulWheelGame,
  "tess-poker": TessPokerGame,
  "hyper-lottery": HyperLotteryGame,
};

export function CasinoGameView({ gameId }: { gameId: string }) {
  const Component = GAME_MAP[gameId];
  if (!Component) return <p className="text-center text-[var(--accent-red)]">Game not found</p>;
  return <Component />;
}
