"use client";

import { SpotTrading } from "@/components/cefi/spot-trading";
import { OrderBook } from "@/components/cefi/order-book";
import { DexSwap } from "@/components/defi/wallet-swap";
import { usePlatformStore } from "@/store/platform";

export default function TradePage() {
  const { mode } = usePlatformStore();

  return (
    <div className="mx-auto max-w-6xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">TessExchange</h1>
      {mode === "centralized" ? (
        <div className="grid grid-cols-3 gap-4">
          <div className="col-span-2"><SpotTrading /></div>
          <OrderBook />
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <DexSwap />
          <OrderBook />
        </div>
      )}
    </div>
  );
}
