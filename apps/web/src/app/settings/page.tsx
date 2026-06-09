"use client";

import { useEffect, useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { usePlatformStore } from "@/store/platform";
import { toastAction } from "@/hooks/use-toast-action";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";

interface Prefs {
  kyc_visible: boolean;
  anonymous_mode: boolean;
  two_factor: boolean;
  tor_routing: boolean;
  zk_disclosure: boolean;
}

export default function SettingsPage() {
  const { tessId } = usePlatformStore();
  const qc = useQueryClient();
  const { data, isLoading } = useQuery({ queryKey: queryKeys.identity(tessId), queryFn: () => api.identity.get(tessId) });
  const [prefs, setPrefs] = useState<Prefs>({ kyc_visible: true, anonymous_mode: false, two_factor: true, tor_routing: false, zk_disclosure: false });

  useEffect(() => {
    if (data?.preferences) setPrefs(data.preferences as Prefs);
  }, [data]);

  const save = async () => {
    await toastAction(
      () => api.identity.updatePreferences(tessId, prefs),
      { success: "Settings saved" }
    );
    qc.invalidateQueries({ queryKey: queryKeys.identity(tessId) });
  };

  const toggle = (key: keyof Prefs) => setPrefs((p) => ({ ...p, [key]: !p[key] }));

  if (isLoading) return <LoadingSpinner />;

  const attestations = data?.attestations as { type: string; issuer: string; verified: boolean }[] || [];

  return (
    <div className="mx-auto max-w-3xl space-y-4 animate-fade-in">
      <h1 className="text-xl font-bold neon-text-cyan">Settings</h1>
      <UnthinkablePanel dapp="settings" action="reality-config" />

      <GlassPanel title="TessID & Attestations">
        <p className="font-mono text-sm text-[var(--accent-cyan)]">{data?.tess_id as string}</p>
        <p className="text-xs text-[var(--text-muted)]">Tier: {data?.tier as string}</p>
        <div className="mt-3 space-y-2">
          {attestations.map((a) => (
            <div key={a.type} className="flex items-center justify-between text-xs">
              <span>{a.type} — {a.issuer}</span>
              <span className={a.verified ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]"}>{a.verified ? "Verified" : "Pending"}</span>
            </div>
          ))}
        </div>
      </GlassPanel>

      <GlassPanel title="Privacy & Security">
        <div className="space-y-3 text-sm">
          {([
            ["kyc_visible", "Show KYC attestation"],
            ["anonymous_mode", "Anonymous mode"],
            ["two_factor", "Two-factor authentication"],
            ["tor_routing", "Tor routing for transactions"],
            ["zk_disclosure", "ZK selective disclosure"],
          ] as [keyof Prefs, string][]).map(([key, label]) => (
            <label key={key} className="flex cursor-pointer items-center justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-3">
              <span>{label}</span>
              <input type="checkbox" checked={prefs[key]} onChange={() => toggle(key)} className="accent-[var(--accent-cyan)]" />
            </label>
          ))}
          <button onClick={save} className="btn-primary btn-cefi w-full">Save Settings</button>
        </div>
      </GlassPanel>
    </div>
  );
}
