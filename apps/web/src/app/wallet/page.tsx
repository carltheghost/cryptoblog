"use client";

import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { NonCustodialWallet, DexSwap } from "@/components/defi/wallet-swap";
import { LivingRelicsGrid } from "@/components/defi/pools-relics-bridge";
import { TesseractCore } from "@/components/hybrid/tesseract-core";
import { cn } from "@/lib/utils";
import { toastAction } from "@/hooks/use-toast-action";
import { api, queryKeys } from "@/lib/api";

export default function WalletPage() {
  const [mode, setMode] = useState<"simple" | "deep">("simple");
  const [batchAction, setBatchAction] = useState("bridge");
  const [batchAmount, setBatchAmount] = useState("100");
  const qc = useQueryClient();

  const { data: config, isLoading } = useQuery({
    queryKey: queryKeys.walletConfig,
    queryFn: () => api.wallet.config(),
    enabled: mode === "deep",
  });

  const [agents, setAgents] = useState({ pricebot: true, rebalancer: false });

  useEffect(() => {
    if (config?.agent_plugins) setAgents(config.agent_plugins);
  }, [config]);

  const setupMultisig = async () => {
    await toastAction(() => api.wallet.setupMultisig({ threshold: 2 }), {
      success: "Multisig wallet activated — 2-of-3 signatures required",
    });
    qc.invalidateQueries({ queryKey: queryKeys.walletConfig });
  };

  const setupRecovery = async () => {
    await toastAction(() => api.wallet.setupRecovery(), {
      success: "Social recovery configured with 3 guardians",
    });
    qc.invalidateQueries({ queryKey: queryKeys.walletConfig });
  };

  const togglePlugin = async (key: "pricebot" | "rebalancer") => {
    const next = { ...agents, [key]: !agents[key] };
    setAgents(next);
    await toastAction(() => api.wallet.updatePlugins({ [key]: next[key] }), {
      success: `${key} ${next[key] ? "enabled" : "disabled"}`,
    });
  };

  const addBatch = async () => {
    const amount = parseFloat(batchAmount);
    if (!amount || amount <= 0) return;
    await toastAction(
      () => api.wallet.addBatch({ action: batchAction, amount, token: "MGANGA", target: "hybrid" }),
      { success: `Queued ${batchAction} for ${amount} MGANGA` }
    );
    qc.invalidateQueries({ queryKey: queryKeys.walletConfig });
  };

  const executeBatch = async () => {
    await toastAction(() => api.wallet.executeBatch(), {
      success: "Batch executed atomically across CeFi + DeFi",
    });
    qc.invalidateQueries({ queryKey: queryKeys.walletConfig });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">Quark Wallet</h1>
        <div className="flex gap-2">
          <button onClick={() => setMode("simple")} className={cn("rounded-lg px-4 py-2 text-xs font-bold transition-all", mode === "simple" ? "bg-[var(--accent-cyan)] text-black" : "text-[var(--text-muted)]")}>Simple Mode</button>
          <button onClick={() => setMode("deep")} className={cn("rounded-lg px-4 py-2 text-xs font-bold transition-all", mode === "deep" ? "bg-[var(--accent-violet)] text-white" : "text-[var(--text-muted)]")}>Deep Mode</button>
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
      ) : isLoading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <GlassPanel title="Multi-Signature Accounts">
            <p className="text-xs text-[var(--text-muted)]">
              {config?.multisig.enabled
                ? `${config.multisig.threshold}-of-${config.multisig.keys_required} multisig active`
                : "Create 2-of-3 multisig wallets with device keys for institutional-grade security."}
            </p>
            <button onClick={setupMultisig} className="btn-primary btn-defi mt-2">
              {config?.multisig.enabled ? "Reconfigure Multisig" : "Create Multisig"}
            </button>
          </GlassPanel>
          <GlassPanel title="Social Recovery">
            <p className="text-xs text-[var(--text-muted)]">
              {config?.recovery.configured
                ? `${config.recovery.guardians.length} guardians configured`
                : "Add trusted TessID contacts who can help recover your keys."}
            </p>
            {config?.recovery.guardians?.map((g) => (
              <p key={g} className="mt-1 font-mono text-[10px] text-[var(--accent-cyan)]">{g}</p>
            ))}
            <button onClick={setupRecovery} className="btn-primary btn-cefi mt-2">
              {config?.recovery.configured ? "Update Guardians" : "Setup Recovery"}
            </button>
          </GlassPanel>
          <GlassPanel title="AI Agent Plugins" variant="violet">
            <div className="space-y-2 text-xs">
              {([
                ["pricebot", "Pricebot", "Auto-scouts market prices"],
                ["rebalancer", "Portfolio Rebalancer", "Rebalances on conditions"],
              ] as ["pricebot" | "rebalancer", string, string][]).map(([key, name, desc]) => (
                <label key={key} className="flex cursor-pointer items-center justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-2">
                  <div>
                    <span className="font-semibold">{name}</span>
                    <p className="text-[10px] text-[var(--text-muted)]">{desc}</p>
                  </div>
                  <input type="checkbox" checked={agents[key]} onChange={() => togglePlugin(key)} />
                </label>
              ))}
            </div>
          </GlassPanel>
          <GlassPanel title="Privacy Controls">
            <div className="space-y-2 text-xs">
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={config?.privacy.pseudonym_mode} readOnly />
                Pseudonym mode
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={config?.privacy.zk_disclosure} readOnly />
                ZK selective disclosure
              </label>
              <label className="flex items-center gap-2">
                <input type="checkbox" checked={config?.privacy.tor_routing} readOnly />
                Tor routing
              </label>
              <p className="text-[10px] text-[var(--text-muted)]">Sync privacy toggles in Settings</p>
            </div>
          </GlassPanel>
          <GlassPanel title="Batch Transactions" className="col-span-2">
            <p className="text-xs text-[var(--text-muted)]">Queue multiple transactions for atomic execution across CeFi and DeFi.</p>
            <div className="mt-2 flex gap-2">
              <select value={batchAction} onChange={(e) => setBatchAction(e.target.value)} className="input-field flex-1">
                <option value="bridge">HYB Bridge</option>
                <option value="swap">DEX Swap</option>
                <option value="stake">Stake</option>
                <option value="transfer">Transfer</option>
              </select>
              <input value={batchAmount} onChange={(e) => setBatchAmount(e.target.value)} className="input-field w-28" type="number" min="1" />
              <button onClick={addBatch} className="btn-primary btn-cefi">Queue</button>
              <button onClick={executeBatch} className="btn-primary btn-defi" disabled={!config?.batch_queue?.length}>
                Execute ({config?.batch_queue?.length || 0})
              </button>
            </div>
            {config?.batch_queue?.length ? (
              <div className="mt-3 space-y-1 text-[10px]">
                {config.batch_queue.map((tx) => (
                  <div key={tx.id} className="flex justify-between rounded bg-[rgba(0,0,0,0.2)] px-2 py-1">
                    <span>{tx.action} · {tx.amount} {tx.token}</span>
                    <span className="text-[var(--accent-gold)]">{tx.status}</span>
                  </div>
                ))}
              </div>
            ) : null}
          </GlassPanel>
        </div>
      )}
    </div>
  );
}
