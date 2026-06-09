"use client";

import { useState } from "react";
import { Shield, Check, Copy } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";
import { toast } from "sonner";

interface Proof {
  algorithm: string;
  server_seed_hash: string;
  client_seed: string;
  nonce: number;
  digest: string;
  game: string;
}

export function RfsamProof({ proof, betId }: { proof?: Proof; betId?: number }) {
  const [verified, setVerified] = useState<boolean | null>(null);
  const [verifying, setVerifying] = useState(false);

  if (!proof) return null;

  const verify = async () => {
    if (!betId) return;
    setVerifying(true);
    try {
      const res = await api.casino.verifyProof(betId);
      setVerified(res.valid as boolean);
      if (res.valid) toast.success("RF-SAM proof verified on-chain ready");
      else toast.error("Proof verification failed");
    } catch {
      toast.error("Verification failed");
    }
    setVerifying(false);
  };

  const copy = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  return (
    <GlassPanel title="RF-SAM Proof" variant="gold" className="text-[10px]">
      <div className="mb-2 flex items-center gap-2 text-xs text-[var(--accent-gold)]">
        <Shield className="h-4 w-4" />
        Random Fair Seed Attestation Module
      </div>
      <div className="space-y-1 font-mono text-[9px] text-[var(--text-muted)]">
        <div className="flex justify-between gap-2">
          <span>Algorithm</span><span className="text-white">{proof.algorithm}</span>
        </div>
        <div className="flex justify-between gap-2">
          <span>Nonce</span><span className="text-[var(--accent-cyan)]">{proof.nonce}</span>
        </div>
        <div className="flex items-center justify-between gap-2">
          <span>Seed Hash</span>
          <button onClick={() => copy(proof.server_seed_hash)} className="flex items-center gap-1 text-[var(--accent-violet)] hover:underline">
            {proof.server_seed_hash.slice(0, 12)}... <Copy className="h-2 w-2" />
          </button>
        </div>
        <div className="flex items-center justify-between gap-2">
          <span>Digest</span>
          <button onClick={() => copy(proof.digest)} className="flex items-center gap-1 text-[var(--accent-cyan)] hover:underline">
            {proof.digest.slice(0, 12)}... <Copy className="h-2 w-2" />
          </button>
        </div>
      </div>
      {betId && (
        <button onClick={verify} disabled={verifying} className="btn-primary btn-cefi mt-2 w-full text-[10px]">
          {verified === true ? <><Check className="inline h-3 w-3" /> Verified</> : verifying ? "Verifying..." : "Verify RF-SAM Proof"}
        </button>
      )}
    </GlassPanel>
  );
}
