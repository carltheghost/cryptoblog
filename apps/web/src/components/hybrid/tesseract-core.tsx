"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { Copy, ArrowLeftRight, Check } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { formatUsd } from "@/lib/utils";
import { toastAction } from "@/hooks/use-toast-action";
import { toast } from "sonner";

export function TesseractCore() {
  const qc = useQueryClient();
  const [bridgeAmount, setBridgeAmount] = useState("100");
  const [showBridge, setShowBridge] = useState(false);
  const [copied, setCopied] = useState(false);
  const [bridging, setBridging] = useState(false);

  const { data: balances, isLoading } = useQuery({
    queryKey: queryKeys.hybridBalances,
    queryFn: () => api.identity.hybridBalances(),
    refetchInterval: 10000,
  });

  const copyId = () => {
    if (balances?.tess_id) {
      navigator.clipboard.writeText(balances.tess_id);
      setCopied(true);
      toast.success("TessID copied!");
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const bridge = async (direction: "cefi_to_defi" | "defi_to_cefi") => {
    setBridging(true);
    const result = await toastAction(
      () => api.defi.bridge({ direction, amount: parseFloat(bridgeAmount) }),
      {
        loading: "Bridging assets...",
        success: () => `Transfer complete via HYB bridge`,
      }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
      qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
      qc.invalidateQueries({ queryKey: ["defi", "wallet"] });
      setShowBridge(false);
    }
    setBridging(false);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="flex flex-col gap-3">
      <GlassPanel variant="gold" className="text-center animate-fade-in">
        <p className="mb-1 text-[10px] uppercase tracking-widest text-[var(--accent-gold)]">Hybrid Account</p>
        <p className="mb-4 text-xs text-[var(--text-muted)]">One TessID. Two Worlds. Unlimited Possibilities.</p>

        <div className="mx-auto mb-4 flex h-28 w-28 items-center justify-center rounded-full tesseract-glow">
          <div className="tesseract-animate relative h-16 w-16">
            <div className="absolute inset-0 border-2 border-[var(--accent-violet)] opacity-80" />
            <div className="absolute inset-1 border-2 border-[var(--accent-cyan)] opacity-60" style={{ transform: "rotate(45deg)" }} />
            <div className="absolute inset-2 border border-[var(--accent-gold)] opacity-40" style={{ transform: "rotate(90deg)" }} />
          </div>
        </div>

        <div className="mb-3 flex items-center justify-center gap-2">
          <span className="font-mono text-sm text-[var(--accent-cyan)]">{balances?.tess_id}</span>
          <button onClick={copyId} className="text-[var(--text-muted)] transition-colors hover:text-[var(--accent-cyan)]">
            {copied ? <Check className="h-3 w-3 text-[var(--accent-green)]" /> : <Copy className="h-3 w-3" />}
          </button>
        </div>

        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="rounded-lg bg-[rgba(0,242,255,0.08)] p-2 transition-all hover:bg-[rgba(0,242,255,0.12)]">
            <p className="text-[var(--text-muted)]">CeFi Balance</p>
            <p className="font-mono font-bold text-[var(--accent-cyan)]">{formatUsd(balances?.cefi_balance ?? 0)}</p>
          </div>
          <div className="rounded-lg bg-[rgba(138,43,226,0.08)] p-2 transition-all hover:bg-[rgba(138,43,226,0.12)]">
            <p className="text-[var(--text-muted)]">DeFi Balance</p>
            <p className="font-mono font-bold text-[var(--accent-violet)]">{formatUsd(balances?.defi_balance ?? 0)}</p>
          </div>
        </div>

        <button onClick={() => setShowBridge(!showBridge)} className="mt-3 flex w-full items-center justify-center gap-2 rounded-lg bg-[rgba(255,215,0,0.1)] py-2 text-xs text-[var(--accent-gold)] transition-all hover:bg-[rgba(255,215,0,0.2)]">
          <ArrowLeftRight className="h-3 w-3" />
          Move assets between CeFi & DeFi
        </button>

        {showBridge && (
          <div className="mt-2 space-y-2 text-xs animate-fade-in">
            <input value={bridgeAmount} onChange={(e) => setBridgeAmount(e.target.value)} className="input-field" placeholder="Amount" type="number" min="1" />
            <div className="flex gap-2">
              <button onClick={() => bridge("cefi_to_defi")} disabled={bridging} className="btn-primary btn-cefi flex-1">CeFi → DeFi</button>
              <button onClick={() => bridge("defi_to_cefi")} disabled={bridging} className="btn-primary btn-defi flex-1">DeFi → CeFi</button>
            </div>
          </div>
        )}
      </GlassPanel>

      <div className="grid grid-cols-2 gap-2">
        <GlassPanel className="py-3 text-center">
          <p className="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">DAG Fast Payments</p>
          <p className="text-lg font-bold text-[var(--accent-cyan)]">&lt; 1 SEC</p>
          <p className="text-[9px] text-[var(--text-muted)]">{(balances?.dag_finality_ms as number) || 850}ms finality</p>
        </GlassPanel>
        <GlassPanel className="py-3 text-center">
          <p className="text-[9px] uppercase tracking-wider text-[var(--text-muted)]">Settlement</p>
          <p className="text-lg font-bold text-[var(--accent-green)]">100%</p>
          <p className="text-[9px] text-[var(--text-muted)]">Blockchain Secure</p>
        </GlassPanel>
      </div>
    </div>
  );
}
