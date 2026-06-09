"use client";

import { useEffect, useState } from "react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

interface Listing { id: number; title: string; description: string; price: number; currency: string }

export default function MarketPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [showCreate, setShowCreate] = useState(false);
  const [newListing, setNewListing] = useState({ title: "", description: "", price: "", currency: "MGANGA" });

  useEffect(() => { api.market.listings().then(setListings); }, []);

  const purchase = async (id: number) => {
    const res = await api.market.purchase(id);
    alert(`Purchased! Receipt relic: ${(res as { relic_token_id: string }).relic_token_id}`);
    api.market.listings().then(setListings);
  };

  const create = async () => {
    await api.market.createListing({ ...newListing, price: parseFloat(newListing.price) });
    setShowCreate(false);
    api.market.listings().then(setListings);
  };

  return (
    <div className="mx-auto max-w-5xl space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">TessMarket</h1>
        <button onClick={() => setShowCreate(!showCreate)} className="rounded-lg bg-[var(--accent-cyan)] px-4 py-2 text-xs font-bold text-black">+ List Item</button>
      </div>

      {showCreate && (
        <GlassPanel title="Create Listing">
          <div className="space-y-2 text-sm">
            <input placeholder="Title" value={newListing.title} onChange={(e) => setNewListing({ ...newListing, title: e.target.value })} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]" />
            <textarea placeholder="Description" value={newListing.description} onChange={(e) => setNewListing({ ...newListing, description: e.target.value })} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]" />
            <div className="flex gap-2">
              <input placeholder="Price" value={newListing.price} onChange={(e) => setNewListing({ ...newListing, price: e.target.value })} className="flex-1 rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]" />
              <select value={newListing.currency} onChange={(e) => setNewListing({ ...newListing, currency: e.target.value })} className="rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]">
                <option>MGANGA</option><option>MWANJESA</option>
              </select>
            </div>
            <button onClick={create} className="rounded-lg bg-[var(--accent-cyan)] px-4 py-2 text-xs font-bold text-black">Publish</button>
          </div>
        </GlassPanel>
      )}

      <div className="grid grid-cols-3 gap-4">
        {listings.map((l) => (
          <GlassPanel key={l.id}>
            <h3 className="font-semibold text-white">{l.title}</h3>
            <p className="mt-1 text-xs text-[var(--text-muted)]">{l.description}</p>
            <div className="mt-3 flex items-center justify-between">
              <span className="font-mono font-bold text-[var(--accent-cyan)]">{l.price} {l.currency}</span>
              <button onClick={() => purchase(l.id)} className="rounded-lg bg-[var(--accent-violet)] px-3 py-1 text-xs font-bold text-white">Buy</button>
            </div>
          </GlassPanel>
        ))}
      </div>
    </div>
  );
}
