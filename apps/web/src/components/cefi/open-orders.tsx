"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { cn } from "@/lib/utils";

export function OpenOrders() {
  const qc = useQueryClient();
  const { data: orders } = useQuery({ queryKey: queryKeys.cefiOrders, queryFn: () => api.cefi.orders(), refetchInterval: 10000 });

  const open = (orders || []).filter((o) => o.status === "open");

  const cancel = async (id: number) => {
    await toastAction(() => api.cefi.cancelOrder(id), { success: "Order cancelled — funds refunded" });
    qc.invalidateQueries({ queryKey: queryKeys.cefiOrders });
    qc.invalidateQueries({ queryKey: queryKeys.cefiAccount });
    qc.invalidateQueries({ queryKey: queryKeys.hybridBalances });
  };

  if (open.length === 0) return null;

  return (
    <GlassPanel title={`Open Orders (${open.length})`} variant="gold">
      <div className="space-y-1 text-[10px]">
        {open.map((o) => (
          <div key={o.id} className="flex items-center justify-between rounded bg-[rgba(255,215,0,0.08)] px-2 py-1.5">
            <span className={cn(o.side === "buy" ? "text-[var(--accent-green)]" : "text-[var(--accent-red)]")}>{o.side.toUpperCase()}</span>
            <span>{o.pair}</span>
            <span className="font-mono">{o.price}</span>
            <span>{o.amount}</span>
            <button onClick={() => cancel(o.id)} className="text-[var(--accent-red)] hover:underline">Cancel</button>
          </div>
        ))}
      </div>
    </GlassPanel>
  );
}
