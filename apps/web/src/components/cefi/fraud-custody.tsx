"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

export function FraudScore() {
  const [data, setData] = useState({ score: 92, risk_level: "low", recommendation: "Low Risk - Good to trade", factors: [] as { name: string; score: number }[] });

  useEffect(() => { api.cefi.fraudScore().then(setData); }, []);

  const pct = data.score;
  const circumference = 2 * Math.PI * 40;
  const offset = circumference - (pct / 100) * circumference;

  return (
    <GlassPanel title="AI Fraud Score">
      <div className="flex items-center gap-4">
        <div className="relative h-24 w-24">
          <svg className="h-24 w-24 -rotate-90" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(0,242,255,0.1)" strokeWidth="8" />
            <circle cx="50" cy="50" r="40" fill="none" stroke="var(--accent-cyan)" strokeWidth="8"
              strokeDasharray={circumference} strokeDashoffset={offset} strokeLinecap="round" />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-xl font-bold text-[var(--accent-cyan)]">{data.score}</span>
            <span className="text-[8px] text-[var(--text-muted)]">/100</span>
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-[var(--accent-green)]">{data.recommendation}</p>
          <div className="mt-2 space-y-1">
            {data.factors.map((f) => (
              <div key={f.name} className="flex items-center gap-2 text-[10px]">
                <span className="text-[var(--text-muted)]">{f.name}</span>
                <span className="text-[var(--accent-cyan)]">{f.score}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </GlassPanel>
  );
}

export function CustodyVault() {
  const [data, setData] = useState({ allocations: [] as { asset: string; amount: number; storage: string }[], storage_type: "institutional_cold" });

  useEffect(() => { api.cefi.custody().then(setData); }, []);

  return (
    <GlassPanel title="Custody Vault">
      <p className="mb-2 text-[10px] uppercase tracking-wider text-[var(--accent-gold)]">Institutional Grade Cold Storage</p>
      <div className="space-y-1 text-xs">
        {data.allocations.map((a) => (
          <div key={a.asset} className="flex justify-between">
            <span className="font-semibold">{a.asset}</span>
            <span className="font-mono text-[var(--text-muted)]">{a.amount.toLocaleString()}</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function CefiStats() {
  const [stats, setStats] = useState({ volume_24h: 0, open_interest: 0, users_online: 0, uptime: 0 });

  useEffect(() => { api.cefi.stats().then(setStats); }, []);

  const fmt = (n: number) => n >= 1e9 ? `$${(n / 1e9).toFixed(2)}B` : n.toLocaleString();

  return (
    <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
      <div><p className="text-[var(--text-muted)]">24H Volume</p><p className="font-bold text-white">{fmt(stats.volume_24h)}</p></div>
      <div><p className="text-[var(--text-muted)]">Open Interest</p><p className="font-bold text-white">{fmt(stats.open_interest)}</p></div>
      <div><p className="text-[var(--text-muted)]">Users Online</p><p className="font-bold text-white">{stats.users_online.toLocaleString()}</p></div>
      <div><p className="text-[var(--text-muted)]">Uptime</p><p className="font-bold text-[var(--accent-green)]">{stats.uptime}%</p></div>
    </div>
  );
}
