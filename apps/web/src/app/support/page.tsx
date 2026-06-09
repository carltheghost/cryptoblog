"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";
import { UnthinkablePanel } from "@/components/omniverse/unthinkable-panel";
import { cn } from "@/lib/utils";

export default function SupportPage() {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [priority, setPriority] = useState("normal");
  const [expanded, setExpanded] = useState<number | null>(null);
  const qc = useQueryClient();
  const { data: tickets, isLoading } = useQuery({ queryKey: queryKeys.supportTickets, queryFn: () => api.support.tickets() });

  const submit = async () => {
    if (!subject || !message) return;
    const res = await toastAction(
      () => api.support.createTicket({ subject, message, priority }),
      { loading: "Submitting ticket...", success: (r) => (r as { response?: string }).response || "Ticket submitted" }
    );
    if (res) {
      setSubject(""); setMessage("");
      qc.invalidateQueries({ queryKey: queryKeys.supportTickets });
    }
  };

  const closeTicket = async (id: number) => {
    await toastAction(() => api.support.updateTicket(id, { status: "closed" }), { success: "Ticket closed" });
    qc.invalidateQueries({ queryKey: queryKeys.supportTickets });
  };

  return (
    <div className="mx-auto max-w-3xl space-y-4 animate-fade-in">
      <h1 className="text-xl font-bold neon-text-cyan">Support</h1>
      <UnthinkablePanel dapp="support" action="paradox-ticket" />
      <GlassPanel title="Open a Ticket">
        <div className="space-y-3 text-sm">
          <input value={subject} onChange={(e) => setSubject(e.target.value)} className="input-field" placeholder="Subject" />
          <textarea value={message} onChange={(e) => setMessage(e.target.value)} className="input-field min-h-[100px]" placeholder="Describe your issue..." />
          <select value={priority} onChange={(e) => setPriority(e.target.value)} className="input-field">
            <option value="low">Low Priority</option>
            <option value="normal">Normal</option>
            <option value="high">High Priority</option>
            <option value="urgent">Urgent</option>
          </select>
          <button onClick={submit} className="btn-primary btn-cefi w-full">Submit Ticket</button>
        </div>
      </GlassPanel>
      <GlassPanel title="Your Tickets">
        {isLoading ? <LoadingSpinner className="py-4" /> : (
          <div className="space-y-2 text-xs">
            {(tickets || []).length === 0 && <p className="text-[var(--text-muted)]">No tickets yet.</p>}
            {(tickets || []).map((t) => (
              <div key={t.id} className="rounded-lg bg-[rgba(0,0,0,0.2)] p-3">
                <button onClick={() => setExpanded(expanded === t.id ? null : t.id)} className="flex w-full items-center justify-between text-left">
                  <span className="font-semibold">{t.subject}</span>
                  <span className={cn("capitalize", t.status === "open" ? "text-[var(--accent-green)]" : "text-[var(--text-muted)]")}>{t.status}</span>
                </button>
                {expanded === t.id && (
                  <div className="mt-2 space-y-2 border-t border-[var(--border-glow)] pt-2 animate-fade-in">
                    <p className="text-[var(--text-muted)]">{t.message}</p>
                    {t.response && (
                      <p className="rounded bg-[rgba(0,242,255,0.08)] p-2 text-[var(--accent-cyan)]">
                        <strong>Support:</strong> {t.response}
                      </p>
                    )}
                    {t.status !== "closed" && (
                      <button onClick={() => closeTicket(t.id)} className="text-[var(--accent-red)] hover:underline">Close ticket</button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </GlassPanel>
    </div>
  );
}
