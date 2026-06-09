import { GlassPanel } from "@/components/ui/glass-panel";

export default function SupportPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-4">
      <h1 className="text-xl font-bold neon-text-cyan">Support</h1>
      <GlassPanel title="Contact Support">
        <p className="text-sm text-[var(--text-muted)]">24/7 support for CeFi users. DeFi community support via DAO.</p>
        <button className="mt-3 rounded-lg bg-[var(--accent-cyan)] px-4 py-2 text-xs font-bold text-black">Open Ticket</button>
      </GlassPanel>
    </div>
  );
}
