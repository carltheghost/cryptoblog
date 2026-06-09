import { cn } from "@/lib/utils";

interface GlassPanelProps {
  children: React.ReactNode;
  className?: string;
  variant?: "default" | "violet" | "gold" | "green";
  title?: string;
  action?: React.ReactNode;
}

export function GlassPanel({ children, className, variant = "default", title, action }: GlassPanelProps) {
  return (
    <div
      className={cn(
        "glass-panel p-4",
        variant === "violet" && "glass-panel-violet",
        variant === "gold" && "glass-panel-gold",
        variant === "green" && "border-[rgba(0,255,136,0.3)]",
        className
      )}
    >
      {(title || action) && (
        <div className="mb-3 flex items-center justify-between">
          {title && <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">{title}</h3>}
          {action}
        </div>
      )}
      {children}
    </div>
  );
}
