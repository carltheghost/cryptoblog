"use client";

import { useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { NonCustodialWallet, DexSwap } from "@/components/defi/wallet-swap";
import { LivingRelicsGrid } from "@/components/defi/pools-relics-bridge";
import { TesseractCore } from "@/components/hybrid/tesseract-core";
import { cn } from "@/lib/utils";

export default function WalletPage() {
  const [mode, setMode] = useState<"simple" | "deep">("simple");

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">Quark Wallet</h1>
        <div className="flex gap-2">
          <button onClick={() => setMode("simple")} className={cn("rounded-lg px-4 py-2 text-xs font-bold", mode === "simple" ? "bg-[var(--accent-cyan)] text-black" : "text-[var(--text-muted)]")}>Simple Mode</button>
          <button onClick={() => setMode("deep")} className={cn("rounded-lg px-4 py-2 text-xs font-bold", mode === "deep" ? "bg-[var(--accent-violet)] text-white" : "text-[var(--text-muted)]")}>Deep Mode</button>
        </div>
      </div>

      {mode === "simple" ? (
        <div className="grid grid-cols-2 gap-4">
          <TesseractCore />
          <div className="space-y-4">
            <NonCustodialWallet />
            <DexSwap />
            <LivingRelicsGrid />
          </div>
        </div>
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <GlassPanel title="Multi-Signature Accounts">
            <p className="text-xs text-[var(--text-muted)]">Create 2-of-3 multisig wallets with device keys</p>
            <button className="mt-2 rounded-lg bg-[var(--accent-violet)] px-4 py-2 text-xs font-bold text-white">Create Multisig</button>
          </GlassPanel>
          <GlassPanel title="Social Recovery">
            <p className="text-xs text-[var(--text-muted)]">Add trusted contacts for key recovery</p>
            <button className="mt-2 rounded-lg bg-[var(--accent-cyan)] px-4 py-2 text-xs font-bold text-black">Setup Recovery</button>
          </GlassPanel>
          <GlassPanel title="AI Agent Plugins">
            <div className="space-y-2 text-xs">
              <div className="flex justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-2">
                <span>Pricebot</span><span className="text-[var(--accent-green)]">Active</span>
              </div>
              <div className="flex justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-2">
                <span>Portfolio Rebalancer</span><span className="text-[var(--text-muted)]">Idle</span>
              </div>
            </div>
          </GlassPanel>
          <GlassPanel title="Privacy Controls">
            <div className="space-y-2 text-xs">
              <label className="flex items-center gap-2"><input type="checkbox" defaultChecked /> Pseudonym mode</label>
              <label className="flex items-center gap-2"><input type="checkbox" /> Selective disclosure (ZK)</label>
              <label className="flex items-center gap-2"><input type="checkbox" /> Tor routing</label>
            </div>
          </GlassPanel>
          <GlassPanel title="Batch Transactions" className="col-span-2">
            <p className="text-xs text-[var(--text-muted)]">Queue multiple transactions for atomic execution</p>
            <button className="mt-2 rounded-lg border border-[var(--border-glow)] px-4 py-2 text-xs">Open Batch Builder</button>
          </GlassPanel>
        </div>
      )}
    </div>
  );
}
