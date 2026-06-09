"use client";

import { Sidebar } from "./sidebar";
import { MobileNav } from "./mobile-nav";
import { Header } from "./header";
import { PriceTicker } from "./ticker";
import { ChronoRibbon } from "@/components/omniverse/chrono-ribbon";
import { OmniverseLayer } from "@/components/omniverse/omniverse-layer";
import { TesseractField } from "@/components/omniverse/tesseract-field";
import { useOmniverseHydration } from "@/hooks/use-omniverse-hydration";
import { usePlatformStore } from "@/store/platform";
import { useOmniverseStore } from "@/store/omniverse";
import { cn } from "@/lib/utils";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { mode } = usePlatformStore();
  const { dimension, overdrive } = useOmniverseStore();
  useOmniverseHydration();

  return (
    <div
      className={cn(
        "flex h-screen flex-col transition-colors duration-500",
        mode === "centralized" ? "mode-cefi" : "mode-defi"
      )}
    >
      <div className="flex flex-1 overflow-hidden">
        <Sidebar className="hidden md:flex" />
        <div className="flex flex-1 flex-col overflow-hidden pb-16 md:pb-0">
          <Header />
          <TesseractField />
          <main className={cn("omniverse-main flex-1 overflow-y-auto scrollbar-thin p-4", `dim-${dimension}`, overdrive && "overdrive-active", dimension === 99 && "dim-infinite")}>
            <OmniverseLayer>{children}</OmniverseLayer>
          </main>
          <ChronoRibbon />
          <PriceTicker />
        </div>
      </div>
      <MobileNav />
    </div>
  );
}
