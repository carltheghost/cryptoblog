"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { formatCompact } from "@/lib/utils";

export function ChildChain() {
  const [chain, setChain] = useState({ name: "TribeChain Alpha", tvl: 0, block_time: 1.2 });

  useEffect(() => { api.defi.childChain().then(setChain); }, []);

  return (
    <GlassPanel title="Child-Chain" variant="violet">
      <p className="font-semibold text-[var(--accent-violet)]">{chain.name}</p>
      <div className="mt-1 flex justify-between text-xs text-[var(--text-muted)]">
        <span>TVL: {formatCompact(chain.tvl)}</span>
        <span>Block: {chain.block_time}s</span>
      </div>
    </GlassPanel>
  );
}

export function DefiPools() {
  const [pools, setPools] = useState<{ pair: string; tvl: number; apy: number }[]>([]);

  useEffect(() => { api.defi.pools().then(setPools); }, []);

  return (
    <GlassPanel title="DeFi Pools" variant="violet">
      <div className="space-y-2 text-xs">
        {pools.map((p) => (
          <div key={p.pair} className="flex justify-between">
            <span className="font-semibold">{p.pair}</span>
            <span className="text-[var(--accent-green)]">{p.apy}% APY</span>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function LivingRelicsGrid() {
  const [relics, setRelics] = useState<{ token_id: string; name: string; image_url: string; type: string }[]>([]);

  useEffect(() => { api.defi.relics().then(setRelics); }, []);

  return (
    <GlassPanel title="NFT / Game Assets" variant="violet">
      <div className="grid grid-cols-2 gap-2">
        {relics.map((r) => (
          <div key={r.token_id} className="overflow-hidden rounded-lg border border-[rgba(138,43,226,0.2)]">
            <img src={r.image_url} alt={r.name} className="h-16 w-full object-cover" />
            <p className="truncate px-1 py-1 text-[10px] font-semibold">{r.name}</p>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}

export function CrossChainBridge() {
  const [amount, setAmount] = useState("500");
  const [token, setToken] = useState("USDC");

  const bridge = async () => {
    alert(`Bridging ${amount} ${token} from Ethereum → TribeChain...`);
  };

  return (
    <GlassPanel title="Cross-Chain Bridge" variant="violet">
      <div className="space-y-2 text-xs">
        <div className="flex gap-2 text-[var(--text-muted)]">
          <span>Ethereum</span><span>→</span><span className="text-[var(--accent-violet)]">TribeChain</span>
        </div>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]" />
        <select value={token} onChange={(e) => setToken(e.target.value)} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]">
          <option>USDC</option><option>ETH</option><option>TRD</option>
        </select>
        <button onClick={bridge} className="w-full rounded-lg bg-[var(--accent-violet)] py-2 font-bold text-white">Bridge Assets</button>
      </div>
    </GlassPanel>
  );
}
