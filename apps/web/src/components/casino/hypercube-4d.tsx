"use client";

import { cn } from "@/lib/utils";

export function Hypercube4D({ size = 120, active = false, className }: { size?: number; active?: boolean; className?: string }) {
  return (
    <div className={cn("hypercube-4d-scene", className)} style={{ width: size, height: size }}>
      <div className={cn("hypercube-4d", active && "hypercube-4d-active")}>
        {(["w", "x", "y", "z"] as const).map((axis) => (
          <div key={axis} className={`hypercube-face hypercube-${axis}`} />
        ))}
        <div className="hypercube-inner">
          <div className="hypercube-core" />
        </div>
      </div>
    </div>
  );
}

export function Dice3D({ value, rolling }: { value: number; rolling?: boolean }) {
  const dots: Record<number, number[][]> = {
    1: [[1, 1]], 2: [[0, 0], [2, 2]], 3: [[0, 0], [1, 1], [2, 2]],
    4: [[0, 0], [0, 2], [2, 0], [2, 2]], 5: [[0, 0], [0, 2], [1, 1], [2, 0], [2, 2]],
    6: [[0, 0], [0, 1], [0, 2], [2, 0], [2, 1], [2, 2]],
  };
  return (
    <div className={cn("dice-3d-scene", rolling && "dice-rolling")}>
      <div className="dice-3d" style={{ transform: `rotateX(${value * 60}deg) rotateY(${value * 45}deg)` }}>
        <div className="dice-face dice-front">
          <div className="dice-dots">
            {(dots[value] || dots[1]).map(([r, c], i) => (
              <span key={i} className="dice-dot" style={{ gridRow: r + 1, gridColumn: c + 1 }} />
            ))}
          </div>
        </div>
        <div className="dice-face dice-back" />
        <div className="dice-face dice-right" />
        <div className="dice-face dice-left" />
        <div className="dice-face dice-top" />
        <div className="dice-face dice-bottom" />
      </div>
    </div>
  );
}

export function SlotReel3D({ symbol, spinning }: { symbol: string; spinning?: boolean }) {
  return (
    <div className={cn("slot-reel-3d", spinning && "slot-reel-spin")}>
      <div className="slot-reel-inner">
        <span className="slot-symbol">{symbol}</span>
      </div>
    </div>
  );
}

export function RouletteWheel3D({ number, spinning }: { number?: number; spinning?: boolean }) {
  const colors = ["#00ff88", "#ff4466", "#1a1a2e"];
  const segments = 37;
  return (
    <div className={cn("roulette-3d-scene", spinning && "roulette-spinning")}>
      <div className="roulette-wheel">
        {Array.from({ length: segments }).map((_, i) => (
          <div
            key={i}
            className="roulette-segment"
            style={{
              transform: `rotate(${(360 / segments) * i}deg)`,
              background: i === 0 ? colors[0] : i % 2 === 0 ? colors[1] : colors[2],
            }}
          />
        ))}
        <div className="roulette-center">
          <span className="text-lg font-bold">{number ?? "?"}</span>
        </div>
      </div>
    </div>
  );
}

export function CrashRocket4D({ multiplier, crashed }: { multiplier: number; crashed?: boolean }) {
  return (
    <div className="crash-4d-scene">
      <div className="crash-orbit-ring" />
      <div className="crash-orbit-ring crash-orbit-ring-2" />
      <div className={cn("crash-rocket", crashed && "crash-explode")} style={{ bottom: `${Math.min(multiplier * 8, 80)}%` }}>
        🚀
      </div>
      <div className="crash-multiplier-display">{multiplier.toFixed(2)}x</div>
    </div>
  );
}
