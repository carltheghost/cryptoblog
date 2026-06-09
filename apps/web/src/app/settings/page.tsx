import { GlassPanel } from "@/components/ui/glass-panel";

export default function SettingsPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Settings</h1>
      <GlassPanel title="TessID & Privacy">
        <div className="space-y-2 text-sm">
          <label className="flex items-center gap-2"><input type="checkbox" defaultChecked /> KYC attestation visible</label>
          <label className="flex items-center gap-2"><input type="checkbox" /> Anonymous mode</label>
          <label className="flex items-center gap-2"><input type="checkbox" defaultChecked /> Two-factor authentication</label>
        </div>
      </GlassPanel>
    </div>
  );
}
