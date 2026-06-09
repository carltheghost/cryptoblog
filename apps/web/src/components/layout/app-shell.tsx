"use client";

import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { PriceTicker } from "./ticker";
import { ChronoRibbon } from "@/components/omniverse/chrono-ribbon";
import { OmniverseLayer } from "@/components/omniverse/omniverse-layer";
import { usePlatformStore } from "@/store/platform";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { mode } = usePlatformStore();

  return (
    <div
      className={cn(
        "flex h-screen flex-col transition-colors duration-500",
        mode === "centralized" ? "mode-cefi" : "mode-defi"
      )}
    >
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <div className="flex flex-1 flex-col overflow-hidden">
          <Header />
          <main className="flex-1 overflow-y-auto scrollbar-thin p-4">
            <OmniverseLayer>{children}</OmniverseLayer>
          </main>
          <ChronoRibbon />
          <PriceTicker />
        </div>
      </div>
    </div>
  );
}
