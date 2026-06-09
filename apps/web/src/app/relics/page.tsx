"use client";

import { useRef, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function RelicsPage() {
  const qc = useQueryClient();
  const fileRef = useRef<HTMLInputElement>(null);
  const { data: relics, isLoading } = useQuery({ queryKey: queryKeys.defiRelics, queryFn: () => api.defi.relics() });
  const [showMint, setShowMint] = useState(false);
  const [form, setForm] = useState({ name: "", description: "", relic_type: "character", image_url: "" });
  const [uploading, setUploading] = useState(false);

  const upload = async (file: File) => {
    setUploading(true);
    try {
      const res = await api.storage.upload(file);
      setForm((f) => ({ ...f, image_url: `https://api.dicebear.com/7.x/shapes/svg?seed=${(res as { cid: string }).cid}` }));
    } catch { /* fallback */ }
    setUploading(false);
  };

  const mint = async () => {
    if (!form.name) return;
    await toastAction(() => api.defi.mintRelic(form), {
      loading: "Submitting relic for validation...",
      success: "Relic submitted! Validators will review shortly.",
    });
    setShowMint(false);
    setForm({ name: "", description: "", relic_type: "character", image_url: "" });
    qc.invalidateQueries({ queryKey: queryKeys.defiRelics });
  };

  const validate = async (tokenId: string) => {
    await toastAction(() => api.defi.validateRelic(tokenId), { success: `${tokenId} validated and minted!` });
    qc.invalidateQueries({ queryKey: queryKeys.defiRelics });
  };

  const shadowProof = async (tokenId: string) => {
    await toastAction(() => api.storage.shadowProof(tokenId), { success: "Shadow proof recorded on-chain" });
    qc.invalidateQueries({ queryKey: queryKeys.defiRelics });
  };

  const list = relics || [];

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-violet">Living Relics Studio</h1>
        <div className="flex gap-2">
          <UnthinkablePanel dapp="relics" action="soul-bind" compact />
          <button onClick={() => setShowMint(!showMint)} className="btn-primary btn-defi">+ Capture Relic</button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-2 text-center text-[10px]">
        {["Capture", "Validate", "Mint", "Trade"].map((step, i) => (
          <div key={step} className={cn("rounded-lg py-2", i <= 2 ? "bg-[rgba(138,43,226,0.15)] text-[var(--accent-violet)]" : "bg-[rgba(255,255,255,0.05)] text-[var(--text-muted)]")}>
            {i + 1}. {step}
          </div>
        ))}
      </div>

      {showMint && (
        <GlassPanel title="Capture → Validate → Mint" variant="violet">
          <div className="space-y-2 text-sm">
            <input placeholder="Relic Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} className="input-field" />
            <textarea placeholder="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} className="input-field min-h-[80px]" />
            <select value={form.relic_type} onChange={(e) => setForm({ ...form, relic_type: e.target.value })} className="input-field">
              {["character", "weapon", "creature", "land", "receipt"].map((t) => <option key={t} value={t}>{t}</option>)}
            </select>
            <input type="file" ref={fileRef} className="hidden" accept="image/*" onChange={(e) => e.target.files?.[0] && upload(e.target.files[0])} />
            <button onClick={() => fileRef.current?.click()} className="btn-primary w-full bg-[rgba(138,43,226,0.15)] text-[var(--accent-violet)]">
              {uploading ? "Uploading to TessStorage..." : "Upload Media to IPFS"}
            </button>
            <button onClick={mint} className="btn-primary btn-defi w-full">Submit for Validation</button>
          </div>
        </GlassPanel>
      )}

      {isLoading ? <LoadingSpinner /> : (
        <div className="grid grid-cols-2 gap-4">
          {list.map((r) => (
            <GlassPanel key={r.token_id} variant="violet">
              <div className="flex gap-3">
                <img src={r.image_url} alt={r.name} className="h-20 w-20 rounded-lg object-cover" />
                <div className="flex-1">
                  <h3 className="font-semibold">{r.name}</h3>
                  <p className="text-[10px] text-[var(--text-muted)]">{r.token_id} · {r.type}</p>
                  <p className="mt-1 text-xs text-[var(--text-muted)] line-clamp-2">{r.description}</p>
                  <div className="mt-2 flex items-center justify-between text-[10px]">
                    <span>Soul Reserve: <span className="text-[var(--accent-gold)]">{r.soul_reserve} TRD</span></span>
                    <span className={cn(
                      r.status === "minted" ? "text-[var(--accent-green)]" :
                      r.status === "pending" ? "text-[var(--accent-gold)]" : "text-[var(--accent-red)]"
                    )}>{r.status}</span>
                  </div>
                  <div className="mt-2 flex gap-2">
                    {r.status === "pending" && (
                      <button onClick={() => validate(r.token_id)} className="text-[10px] text-[var(--accent-violet)] hover:underline">Validate</button>
                    )}
                    <button onClick={() => shadowProof(r.token_id)} className="text-[10px] text-[var(--text-muted)] hover:text-[var(--accent-red)]">Shadow Proof</button>
                  </div>
                </div>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
