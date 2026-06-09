"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

interface Entry { price: number; amount: number }

export function OrderBook() {
  const [bids, setBids] = useState<Entry[]>([]);
  const [asks, setAsks] = useState<Entry[]>([]);

  useEffect(() => {
    const load = () => api.cefi.orderbook("BTC/USDT").then((d: { bids: Entry[]; asks: Entry[] }) => {
      setBids(d.bids); setAsks(d.asks);
    });
    load();
    const interval = setInterval(load, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <GlassPanel title="Order Book">
      <div className="space-y-0.5 text-xs font-mono">
        {asks.slice().reverse().map((a, i) => (
          <div key={`a${i}`} className="flex justify-between text-[var(--accent-red)]">
            <span>{a.price.toFixed(2)}</span>
            <span className="text-[var(--text-muted)]">{a.amount.toFixed(4)}</span>
          </div>
        ))}
        <div className="my-1 border-t border-[var(--border-glow)] py-1 text-center text-[var(--accent-cyan)]">
          {bids[0]?.price.toFixed(2) || "—"}
        </div>
        {bids.map((b, i) => (
          <div key={`b${i}`} className="flex justify-between text-[var(--accent-green)]">
            <span>{b.price.toFixed(2)}</span>
            <span className="text-[var(--text-muted)]">{b.amount.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
