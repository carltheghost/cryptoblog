"use client";

import { useEffect, useState } from "react";
import { Copy, ArrowLeftRight } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { formatUsd } from "@/lib/utils";
import { usePlatformStore } from "@/store/platform";

export function TesseractCore() {
  const { tessId } = usePlatformStore();
  const [balances, setBalances] = useState({
    tess_id: tessId, cefi_balance: 0, defi_balance: 0, hyb_balance: 0,
    dag_finality_ms: 850, settlement_secure: true,
  });
  const [bridgeAmount, setBridgeAmount] = useState("100");
  const [showBridge, setShowBridge] = useState(false);

  const load = () => api.identity.hybridBalances().then(setBalances);
  useEffect(() => { load(); }, []);

  const copyId = () => { navigator.clipboard.writeText(balances.tess_id); };

  const bridge = async (direction: "cefi_to_defi" | "defi_to_cefi") => {
    await api.defi.bridge({ direction, amount: parseFloat(bridgeAmount) });
    load();
    setShowBridge(false);
    alert("Bridge transfer completed!");
  };

  return (
    <div className="flex flex-col gap-3">
      <GlassPanel variant="gold" className="text-center">
        <p className="mb-3 text-[10px] uppercase tracking-widest text-[var(--accent-gold)]">Hybrid Account</p>
        <p className="mb-4 text-xs text-[var(--text-muted)]">One TessID. Two Worlds. Unlimited Possibilities.</p>

        <div className="mx-auto mb-4 flex h-28 w-28 items-center justify-center rounded-full tesseract-glow">
          <div className="tesseract-animate relative h-16 w-16">
            <div className="absolute inset-0 border-2 border-[var(--accent-violet)] opacity-80" style={{ transform: "translateZ(8px)" }} />
            <div className="absolute inset-1 border-2 border-[var(--accent-cyan)] opacity-60" style={{ transform: "rotate(45deg) translateZ(-8px)" }} />
            <div className="absolute inset-2 border border-[var(--accent-gold)] opacity-40" style={{ transform: "rotate(90deg)" }} />
          </div>
        </div>

        <div className="mb-3 flex items-center justify-center gap-2">
          <span className="font-mono text-sm text-[var(--accent-cyan)]">{balances.tess_id}</span>
          <button onClick={copyId} className="text-[var(--text-muted)] hover:text-[var(--accent-cyan)]"><Copy className="h-3 w-3" /></button>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-[rgba(0,242,255,0.08)] p-2">
            <p className="text-[var(--text-muted)]">CeFi Balance</p>
            <p className="font-mono font-bold text-[var(--accent-cyan)]">{formatUsd(balances.cefi_balance)}</p>
          </div>
          <div className="rounded-lg bg-[rgba(138,43,226,0.08)] p-2">
            <p className="text-[var(--text-muted)]">DeFi Balance</p>
            <p className="font-mono font-bold text-[var(--accent-violet)]">{formatUsd(balances.defi_balance)}</p>
          </div>
        </div>

        <button onClick={() => setShowBridge(!showBridge)} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-[rgba(255,215,0,0.1)] py-2 text-xs text-[var(--accent-gold)] hover:bg-[rgba(255,215,0,0.2)]">
          <ArrowLeftRight className="h-3 w-3" />
          Move assets between CeFi & DeFi
        </button>

        {showBridge && (
          <div className="mt-2 space-y-2 text-xs">
            <input value={bridgeAmount} onChange={(e) => setBridgeAmount(e.target.value)} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]" placeholder="Amount" />
            <div className="flex gap-2">
              <button onClick={() => bridge("cefi_to_defi")} className="flex-1 rounded-lg bg-[var(--accent-cyan)] py-2 font-bold text-black">CeFi → DeFi</button>
              <button onClick={() => bridge("defi_to_cefi")} className="flex-1 rounded-lg bg-[var(--accent-violet)] py-2 font-bold text-white">DeFi → CeFi</button>
            </div>
          </div>
        )}
      </GlassPanel>

      <div className="grid grid-cols-2 gap-2">
        <GlassPanel className="text-center py-3">
          <p className="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">DAG Fast Payments</p>
          <p className="text-lg font-bold text-[var(--accent-cyan)]">&lt; 1 SEC</p>
          <p className="text-[9px] text-[var(--text-muted)]">Avg. Finality</p>
        </GlassPanel>
        <GlassPanel className="text-center py-3">
          <p className="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">Blockchain Settlement</p>
          <p className="text-lg font-bold text-[var(--accent-green)]">100%</p>
          <p className="text-[9px] text-[var(--text-muted)]">Secure</p>
        </GlassPanel>
      </div>
    </div>
  );
}
