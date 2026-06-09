"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

export default function MarketPage() {
  const qc = useQueryClient();
  const { data: listings, isLoading } = useQuery({ queryKey: queryKeys.marketListings, queryFn: () => api.market.listings() });
  const [showCreate, setShowCreate] = useState(false);
  const [showBarter, setShowBarter] = useState(false);
  const [newListing, setNewListing] = useState({ title: "", description: "", price: "", currency: "MGANGA" });
  const [barterOffer, setBarterOffer] = useState("");
  const [barterRequest, setBarterRequest] = useState("");

  const purchase = async (id: number) => {
    await toastAction(() => api.market.purchase(id), {
      loading: "Processing purchase...",
      success: (r) => `Purchased! Receipt: ${(r as { relic_token_id: string }).relic_token_id}`,
    });
    qc.invalidateQueries({ queryKey: queryKeys.marketListings });
    qc.invalidateQueries({ queryKey: queryKeys.defiRelics });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  const create = async () => {
    if (!newListing.title || !newListing.price) return;
    await toastAction(
      () => api.market.createListing({ ...newListing, price: parseFloat(newListing.price) }),
      { success: "Listing published!" }
    );
    setShowCreate(false);
    qc.invalidateQueries({ queryKey: queryKeys.marketListings });
  };

  const barter = async () => {
    await toastAction(
      () => api.market.barter({ offer_assets: barterOffer.split(",").map((s) => s.trim()), request_assets: barterRequest.split(",").map((s) => s.trim()) }),
      { success: "Barter offer created!" }
    );
    setShowBarter(false);
  };

  const list = listings || [];

  return (
    <div className="mx-auto max-w-5xl space-y-4 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold neon-text-cyan">TessMarket</h1>
        <div className="flex items-center gap-2">
          <UnthinkablePanel dapp="market" action="barter-paradox" compact />
          <button onClick={() => setShowBarter(!showBarter)} className="btn-primary bg-[rgba(138,43,226,0.2)] text-[var(--accent-violet)]">Barter</button>
          <button onClick={() => setShowCreate(!showCreate)} className="btn-primary btn-cefi">+ List Item</button>
        </div>
      </div>

      <UnthinkablePanel dapp="market" action="soul-commerce" />

      {showCreate && (
        <GlassPanel title="Create Listing">
          <div className="space-y-2 text-sm">
            <input placeholder="Title" value={newListing.title} onChange={(e) => setNewListing({ ...newListing, title: e.target.value })} className="input-field" />
            <textarea placeholder="Description" value={newListing.description} onChange={(e) => setNewListing({ ...newListing, description: e.target.value })} className="input-field min-h-[80px]" />
            <div className="flex gap-2">
              <input placeholder="Price" value={newListing.price} onChange={(e) => setNewListing({ ...newListing, price: e.target.value })} className="input-field flex-1" type="number" />
              <select value={newListing.currency} onChange={(e) => setNewListing({ ...newListing, currency: e.target.value })} className="input-field">
                <option>MGANGA</option><option>MWANJESA</option>
              </select>
            </div>
            <button onClick={create} className="btn-primary btn-cefi">Publish</button>
          </div>
        </GlassPanel>
      )}

      {showBarter && (
        <GlassPanel title="Barter Swap" variant="violet">
          <div className="space-y-2 text-sm">
            <input placeholder="Offer assets (comma separated)" value={barterOffer} onChange={(e) => setBarterOffer(e.target.value)} className="input-field" />
            <input placeholder="Request assets (comma separated)" value={barterRequest} onChange={(e) => setBarterRequest(e.target.value)} className="input-field" />
            <button onClick={barter} className="btn-primary btn-defi">Create Barter Offer</button>
          </div>
        </GlassPanel>
      )}

      {isLoading ? <LoadingSpinner /> : (
        <div className="grid grid-cols-3 gap-4">
          {list.map((l) => (
            <GlassPanel key={l.id} className="transition-all hover:border-[var(--accent-cyan)]">
              {l.image_url && <img src={l.image_url} alt={l.title} className="mb-2 h-24 w-full rounded-lg object-cover" />}
              <h3 className="font-semibold">{l.title}</h3>
              <p className="mt-1 text-xs text-[var(--text-muted)] line-clamp-2">{l.description}</p>
              <div className="mt-3 flex items-center justify-between">
                <span className="font-mono font-bold text-[var(--accent-cyan)]">{l.price} {l.currency}</span>
                <button onClick={() => purchase(l.id)} className="btn-primary btn-defi px-3 py-1">Buy</button>
              </div>
            </GlassPanel>
          ))}
        </div>
      )}
    </div>
  );
}
