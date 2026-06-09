"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

interface Order { id: number; pair: string; side: string; type: string; price: number; amount: number; status: string; created_at: string }

export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[]>([]);

  useEffect(() => { api.cefi.orders().then(setOrders); }, []);

  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Order History</h1>
      <GlassPanel>
        <div className="space-y-2 text-xs">
          {orders.length === 0 && <p className="text-[var(--text-muted)]">No orders yet. Place one from the Trade page.</p>}
          {orders.map((o) => (
            <div key={o.id} className="flex items-center justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-3">
              <span className="font-semibold">{o.pair}</span>
              <span className={o.side === "buy" ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}>{o.side.toUpperCase()}</span>
              <span className="font-mono">{o.price.toFixed(2)}</span>
              <span>{o.amount}</span>
              <span className="text-[var(--text-muted)]">{o.status}</span>
            </div>
          ))}
        </div>
      </GlassPanel>
    </div>
  );
}
