"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { GlassPanel } from "@/components/ui/glass-panel";
import { LoadingSpinner } from "@/components/ui/loading";
import { api, queryKeys } from "@/lib/api";
import { toastAction } from "@/hooks/use-toast-action";

export default function SupportPage() {
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");
  const [priority, setPriority] = useState("normal");
  const qc = useQueryClient();
  const { data: tickets, isLoading } = useQuery({ queryKey: queryKeys.supportTickets, queryFn: () => api.support.tickets() });

  const submit = async () => {
    if (!subject || !message) return;
    await toastAction(
      () => api.support.createTicket({ subject, message, priority }),
      { loading: "Submitting ticket...", success: "Ticket submitted — we'll respond within 24h" }
    );
    setSubject(""); setMessage("");
    qc.invalidateQueries({ queryKey: queryKeys.supportTickets });
  };

  return (
    <div className="mx-auto max-w-3xl space-y-4 animate-fade-in">
      <h1 className="text-xl font-bold neon-text-cyan">Support</h1>
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
            {(tickets || []).length === 0 && (
              <p className="text-[var(--text-muted)]">No tickets yet.</p>
            )}
            {(tickets || []).map((t) => (
              <div key={t.id} className="flex items-center justify-between rounded-lg bg-[rgba(0,0,0,0.2)] p-3">
                <span className="font-semibold">{t.subject}</span>
                <span className="text-[var(--text-muted)]">{t.priority}</span>
                <span className="text-[var(--accent-green)]">{t.status}</span>
              </div>
            ))}
          </div>
        )}
      </GlassPanel>
    </div>
  );
}
