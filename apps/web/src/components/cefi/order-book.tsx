"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

interface Entry { price: number; amount: number }

export function OrderBook({ pair = "BTC/USDT" }: { pair?: string }) {
  const [bids, setBids] = useState<Entry[]>([]);
  const [asks, setAsks] = useState<Entry[]>([]);
  const [mid, setMid] = useState(0);

  useEffect(() => {
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000";
    let ws: WebSocket | null = null;
    let pollTimer: ReturnType<typeof setInterval>;

    const loadHttp = () => {
      api.cefi.orderbook(pair).then((d) => {
        setBids(d.bids); setAsks(d.asks);
        if (d.last_price) setMid(d.last_price);
        else if (d.bids[0]) setMid(d.bids[0].price);
      }).catch(() => {});
    };

    try {
      ws = new WebSocket(`${wsUrl}/ws/orderbook/${encodeURIComponent(pair)}`);
      ws.onmessage = (e) => {
        const d = JSON.parse(e.data);
        if (d.bids) setBids(d.bids);
        if (d.asks) setAsks(d.asks);
        if (d.bids?.[0]) setMid(d.bids[0].price);
      };
      ws.onerror = () => { ws?.close(); loadHttp(); pollTimer = setInterval(loadHttp, 3000); };
    } catch {
      loadHttp();
      pollTimer = setInterval(loadHttp, 3000);
    }

    return () => { ws?.close(); clearInterval(pollTimer); };
  }, [pair]);

  const maxBid = Math.max(...bids.map((b) => b.amount), 1);
  const maxAsk = Math.max(...asks.map((a) => a.amount), 1);

  return (
    <GlassPanel title="Order Book" className="animate-fade-in">
      <div className="space-y-0.5 text-xs font-mono">
        {asks.slice().reverse().map((a, i) => (
          <div key={`a${i}`} className="relative flex justify-between text-[var(--accent-red)]">
            <div className="absolute inset-y-0 right-0 bg-[rgba(255,68,102,0.08)]" style={{ width: `${(a.amount / maxAsk) * 100}%` }} />
            <span className="relative z-10">{a.price.toFixed(2)}</span>
            <span className="relative z-10 text-[var(--text-muted)]">{a.amount.toFixed(4)}</span>
          </div>
        ))}
        <div className="my-1 border-t border-[var(--border-glow)] py-1 text-center font-bold text-[var(--accent-cyan)]">
          {mid.toFixed(2)}
        </div>
        {bids.map((b, i) => (
          <div key={`b${i}`} className="relative flex justify-between text-[var(--accent-green)]">
            <div className="absolute inset-y-0 right-0 bg-[rgba(0,255,136,0.08)]" style={{ width: `${(b.amount / maxBid) * 100}%` }} />
            <span className="relative z-10">{b.price.toFixed(2)}</span>
            <span className="relative z-10 text-[var(--text-muted)]">{b.amount.toFixed(4)}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
