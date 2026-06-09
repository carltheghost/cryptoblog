import { cn } from "@/lib/utils";

export function LoadingSpinner({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center justify-center py-8", className)}>
      <div className="h-6 w-6 animate-spin rounded-full border-2 border-[var(--accent-cyan)] border-t-transparent" />
    </div>
  );
}

export function PanelSkeleton() {
  return (
    <div className="glass-panel animate-pulse p-4">
      <div className="mb-3 h-3 w-24 rounded bg-[rgba(255,255,255,0.08)]" />
      <div className="space-y-2">
        <div className="h-4 w-full rounded bg-[rgba(255,255,255,0.05)]" />
        <div className="h-4 w-3/4 rounded bg-[rgba(255,255,255,0.05)]" />
      </div>
    </div>
  );
}
