"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

interface Relic { token_id: string; name: string; description: string; image_url: string; type: string; status: string; soul_reserve: number }

export default function RelicsPage() {
  const [relics, setRelics] = useState<Relic[]>([]);
  const [showMint, setShowMint] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", relic_type: "character" });

  useEffect(() => { api.defi.relics().then(setRelics); }, []);

  const mint = async () => {
    await api.defi.mintRelic(form);
    setShowMint(false);
    api.defi.relics().then(setRelics);
    alert("Relic submitted for validation!");
  };

  const shadowProof = async (tokenId: string) => {
    await api.storage.shadowProof(tokenId);
    alert(`Shadow proof recorded for ${tokenId}`);
  };

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-violet">Living Relics Studio</h1>
        <button onClick={() => setShowMint(!showMint)} className="rounded-lg bg-[var(--accent-violet)] px-4 py-2 text-xs font-bold text-white">+ Capture Relic</button>
      </div>

      {showMint && (
        <GlassPanel title="Capture → Validate → Mint" variant="violet">
          <div className="space-y-2 text-sm">
            <input placeholder="Relic Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]" />
            <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]" />
            <select value={form.relic_type} onChange={(e) => setForm({ ...form, relic_type: e.target.value })} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[rgba(138,43,226,0.3)]">
              <option value="character">Character</option>
              <option value="weapon">Weapon</option>
              <option value="creature">Creature</option>
              <option value="land">Land</option>
              <option value="receipt">Receipt</option>
            </select>
            <button onClick={mint} className="rounded-lg bg-[var(--accent-violet)] px-4 py-2 text-xs font-bold text-white">Submit for Validation</button>
          </div>
        </GlassPanel>
      )}

      <div className="grid grid-cols-2 gap-4">
        {relics.map((r) => (
          <GlassPanel key={r.token_id} variant="violet">
            <div className="flex gap-3">
              <img src={r.image_url} alt={r.name} className="h-20 w-20 rounded-lg object-cover" />
              <div className="flex-1">
                <h3 className="font-semibold">{r.name}</h3>
                <p className="text-[10px] text-[var(--text-muted)]">{r.token_id} · {r.type}</p>
                <p className="mt-1 text-xs text-[var(--text-muted)]">{r.description}</p>
                <div className="mt-2 flex items-center justify-between text-[10px]">
                  <span>Soul Reserve: <span className="text-[var(--accent-gold)]">{r.soul_reserve} TRD</span></span>
                  <span className="text-[var(--accent-green)]">{r.status}</span>
                </div>
                <button onClick={() => shadowProof(r.token_id)} className="mt-1 text-[10px] text-[var(--text-muted)] hover:text-[var(--accent-red)]">Shadow Proof</button>
              </div>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}
