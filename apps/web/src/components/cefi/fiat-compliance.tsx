"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCircle, Shield, XCircle } from "lucide-react";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";

export function FiatDeposit() {
  const [method, setMethod] = useState<"bank_transfer" | "card">("bank_transfer");
  const [amount, setAmount] = useState("1000");
  const [submitting, setSubmitting] = useState(false);
  const qc = useQueryClient();

  const deposit = async () => {
    setSubmitting(true);
    const result = await toastAction(
      () => api.cefi.fiatDeposit({ method, amount: parseFloat(amount), currency: "USD" }),
      {
        loading: "Processing deposit...",
        success: (r) => `Deposited! Balance: $${(r as { new_balance: number }).new_balance.toFixed(2)}`,
      }
    );
    if (result) {
      qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
      qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
    }
    setSubmitting(false);
  };

  return (
    <GlassPanel title="Fiat Deposit" className="animate-fade-in">
      <div className="space-y-2 text-xs">
        <div className="flex gap-2">
          <button onClick={() => setMethod("bank_transfer")} className={`flex-1 rounded-lg py-2 transition-all ${method === "bank_transfer" ? "bg-[rgba(0,242,255,0.15)] text-[var(--accent-cyan)]" : "bg-[rgba(255,255,255,0.05)] text-[var(--text-muted)]"}`}>Bank Transfer</button>
          <button onClick={() => setMethod("card")} className={`flex-1 rounded-lg py-2 transition-all ${method === "card" ? "bg-[rgba(0,242,255,0.15)] text-[var(--accent-cyan)]" : "bg-[rgba(255,255,255,0.05)] text-[var(--text-muted)]"}`}>Card</button>
        </div>
        {method === "card" && <p className="text-[10px] text-[var(--text-muted)]">Instant deposit via Visa/Mastercard (2.5% fee)</p>}
        <input value={amount} onChange={(e) => setAmount(e.target.value)} className="input-field" placeholder="Amount USD" type="number" min="10" />
        <button onClick={deposit} disabled={submitting} className="btn-primary btn-cefi w-full py-2">
          {method === "card" ? "Deposit with Card" : "Deposit via Bank"}
        </button>
      </div>
    </GlassPanel>
  );
}

export function ComplianceStatus() {
  const { data: status, isLoading } = useQuery({
    queryKey: ["cefi", "compliance"],
    queryFn: () => api.cefi.compliance(),
  });

  if (isLoading) return <GlassPanel title="Compliance"><LoadingSpinner className="py-4" /></GlassPanel>;

  const verified = status?.kyc_status === "verified";
  const aml = status?.aml_compliant;

  return (
    <GlassPanel title="Compliance" variant="green" className="animate-fade-in">
      <div className="flex items-center gap-2 text-xs">
        {verified ? <CheckCircle className="h-4 w-4 text-[var(--accent-green)]" /> : <XCircle className="h-4 w-4 text-[var(--accent-red)]" />}
        <span className={verified ? "font-semibold text-[var(--accent-green)]" : "text-[var(--accent-red)]"}>
          KYC {verified ? "Verified" : "Pending"}
        </span>
      </div>
      <div className="mt-1 flex items-center gap-2 text-xs">
        {aml ? <Shield className="h-4 w-4 text-[var(--accent-green)]" /> : <XCircle className="h-4 w-4 text-[var(--accent-red)]" />}
        <span className={aml ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}>
          AML {aml ? "Compliant" : "Review Required"}
        </span>
      </div>
      <p className="mt-2 text-[10px] text-[var(--text-muted)]">Tier: {status?.tier}</p>
    </GlassPanel>
  );
}
