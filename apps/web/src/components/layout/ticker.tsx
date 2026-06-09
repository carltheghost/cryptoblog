"use client";

import { useEffect, useState, useCallback } from "react";
import { cn } from "@/lib/utils";
import { api } from "@/lib/api";

interface TickerPair {
  symbol: string;
  price: number;
  change: number;
}

const DEFAULT: TickerPair[] = [
  { symbol: "BTC/USDT", price: 68432.18, change: 1.92 },
  { symbol: "ETH/USDT", price: 3456.72, change: -0.45 },
  { symbol: "TRD/USDT", price: 0.2457, change: 3.88 },
  { symbol: "SOL/USDT", price: 178.34, change: 2.11 },
  { symbol: "BNB/USDT", price: 612.50, change: 0.78 },
];

export function PriceTicker() {
  const [pairs, setPairs] = useState<TickerPair[]>(DEFAULT);

  const fetchRest = useCallback(async () => {
    try {
      const data = await api.cefi.ticker();
      if (data.pairs) setPairs(data.pairs);
    } catch { /* keep last known */ }
  }, []);

  useEffect(() => {
    fetchRest();
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    let ws: WebSocket | null = null;
    let reconnectTimer: ReturnType<typeof setTimeout>;
    let restTimer: ReturnType<typeof setInterval>;

    const connect = () => {
      try {
        ws = new WebSocket(`${wsUrl}/ws/ticker`);
        ws.onmessage = (e) => {
          const data = JSON.parse(e.data);
          if (data.pairs) setPairs(data.pairs);
        };
        ws.onclose = () => {
          reconnectTimer = setTimeout(connect, 5000);
        };
        ws.onerror = () => ws?.close();
      } catch {
        restTimer = setInterval(fetchRest, 5000);
      }
    };

    connect();
    restTimer = setInterval(fetchRest, 15000);

    return () => {
      ws?.close();
      clearTimeout(reconnectTimer);
      clearInterval(restTimer);
    };
  }, [fetchRest]);

  return (
    <div className="flex h-8 items-center gap-6 overflow-hidden border-t border-[var(--border-glow)] bg-[rgba(5,7,10,0.95)] px-4 text-xs">
      {pairs.map((p) => (
        <div key={p.symbol} className="flex shrink-0 items-center gap-2">
          <span className="font-semibold text-[var(--text-muted)]">{p.symbol}</span>
          <span className="font-mono text-white">
            {p.price < 10 ? p.price.toFixed(4) : p.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
          </span>
          <span className={cn("font-mono", p.change >= 0 ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>
            {p.change >= 0 ? "+" : ""}{p.change.toFixed(2)}%
          </span>
        </div>
      ))}
    </div>
  );
}
