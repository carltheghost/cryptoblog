"use client";

import { useEffect, useState } from "react";
import { CheckCircle, Shield } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api } from "@/lib/api";

export function FiatDeposit() {
  const [amount, setAmount] = useState("1000");

  const deposit = async () => {
    const res = await api.cefi.fiatDeposit({ method: "bank_transfer", amount: parseFloat(amount), currency: "USD" });
    alert(`Deposit completed! New balance: $${(res as { new_balance: number }).new_balance.toFixed(2)}`);
  };

  return (
    <GlassPanel title="Fiat Deposit">
      <div className="space-y-2 text-xs">
        <div className="flex gap-2">
          <button className="flex-1 rounded-lg bg-[rgba(0,242,255,0.1)] py-2 text-[var(--accent-cyan)]">Bank Transfer</button>
          <button className="flex-1 rounded-lg bg-[rgba(255,255,255,0.05)] py-2 text-[var(--text-muted)]">Card</button>
        </div>
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="w-full rounded-lg bg-[rgba(0,0,0,0.3)] px-3 py-2 text-white border border-[var(--border-glow)]" placeholder="Amount USD" />
        <button onClick={deposit} className="w-full rounded-lg bg-[var(--accent-cyan)] py-2 font-bold text-black">Deposit</button>
      </div>
    </GlassPanel>
  );
}

export function ComplianceStatus() {
  const [status, setStatus] = useState({ kyc_status: "verified", aml_compliant: true, tier: "verified" });

  useEffect(() => { api.cefi.compliance().then(setStatus); }, []);

  return (
    <GlassPanel title="Compliance" variant="green">
      <div className="flex items-center gap-2 text-xs">
        <CheckCircle className="h-4 w-4 text-[var(--accent-green)]" />
        <span className="font-semibold text-[var(--accent-green)]">KYC Verified</span>
      </div>
      <div className="mt-1 flex items-center gap-2 text-xs">
        <Shield className="h-4 w-4 text-[var(--accent-green)]" />
        <span className="text-[var(--accent-green)]">AML Compliant</span>
      </div>
      <p className="mt-2 text-[10px] text-[var(--text-muted)]">Tier: {status.tier}</p>
    </GlassPanel>
  );
}
