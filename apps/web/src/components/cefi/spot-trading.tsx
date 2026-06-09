"use client";

import { useEffect, useRef, useState } from "react";
import { createChart, ColorType, IChartApi, CandlestickSeries } from "lightweight-charts";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

export function SpotTrading() {
  const chartRef = useRef<HTMLDivElement>(null);
  const chartInstance = useRef<IChartApi | null>(null);
  const [price, setPrice] = useState(68432.18);
  const [change, setChange] = useState(1.92);
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [amount, setAmount] = useState("0.01");
  const [orderType, setOrderType] = useState("limit");

  useEffect(() => {
    if (!chartRef.current) return;
    const chart = createChart(chartRef.current, {
      layout: { background: { type: ColorType.Solid, color: "transparent" }, textColor: "#7a8ba3" },
      grid: { vertLines: { color: "rgba(0,242,255,0.05)" }, horzLines: { color: "rgba(0,242,255,0.05)" } },
      width: chartRef.current.clientWidth,
      height: 220,
    });
    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#00ff88", downColor: "#ff4466", borderVisible: false,
      wickUpColor: "#00ff88", wickDownColor: "#ff4466",
    });
    chartInstance.current = chart;

    api.cefi.chart("BTC/USDT").then((data: { candles: { open: number; high: number; low: number; close: number; time: number }[] }) => {
      series.setData(data.candles.map((c, i) => ({ ...c, time: i as unknown as import("lightweight-charts").Time })));
      if (data.candles.length) {
        const last = data.candles[data.candles.length - 1];
        setPrice(last.close);
      }
    });

    const ro = new ResizeObserver(() => {
      if (chartRef.current) chart.applyOptions({ width: chartRef.current.clientWidth });
    });
    ro.observe(chartRef.current);
    return () => { chart.remove(); ro.disconnect(); };
  }, []);

  const placeOrder = async () => {
    await api.cefi.placeOrder({
      pair: "BTC/USDT", side, order_type: orderType,
      price: price, amount: parseFloat(amount),
    });
    alert(`${side.toUpperCase()} order placed!`);
  };

  return (
    <GlassPanel title="Spot Trading" className="col-span-2">
      <div className="mb-2 flex items-baseline gap-3">
        <span className="text-lg font-bold text-white">BTC/USDT</span>
        <span className="font-mono text-xl font-bold text-[var(--accent-cyan)]">${price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</span>
        <span className={cn("text-sm font-mono", change >= 0 ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>
          {change >= 0 ? "+" : ""}{change.toFixed(2)}%
        </span>
      </div>
      <div ref={chartRef} className="mb-3 w-full" />
      <div className="flex gap-2">
        <button onClick={() => setSide("buy")} className={cn("flex-1 rounded-lg py-2 text-sm font-bold", side === "buy" ? "bg-[var(--accent-green)] text-black" : "bg-[rgba(0,255,136,0.1)] text-[var(--accent-green)]")}>Buy</button>
        <button onClick={() => setSide("sell")} className={cn("flex-1 rounded-lg py-2 text-sm font-bold", side === "sell" ? "bg-[var(--accent-red)] text-white" : "bg-[rgba(255,68,102,0.1)] text-[var(--accent-red)]")}>Sell</button>
      </div>
      <div className="mt-2 flex gap-2">
        <select value={orderType} onChange={(e) => setOrderType(e.target.value)} className="flex-1 rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-xs text-white border border-[var(--border-glow)]">
          <option value="limit">Limit</option>
          <option value="market">Market</option>
        </select>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="flex-1 rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-xs text-white border border-[var(--border-glow)]" placeholder="Amount" />
        <button onClick={placeOrder} className="rounded-lg bg-[var(--accent-cyan)] px-4 py-2 text-xs font-bold text-black">Place Order</button>
      </div>
    </GlassPanel>
  );
}
