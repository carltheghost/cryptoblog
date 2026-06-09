"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  ArrowLeftRight,
  Wallet,
  ListOrdered,
  History,
  Gift,
  BarChart3,
  Headphones,
  Settings,
  Hexagon,
  Gem,
  Bot,
} from "lucide-react";
import { cn } from "@/lib/utils";

const navItems = [
  { href: "/", icon: LayoutDashboard, label: "Dashboard" },
  { href: "/trade", icon: TrendingUp, label: "Trade" },
  { href: "/wallet", icon: Wallet, label: "Quark Wallet" },
  { href: "/market", icon: ArrowLeftRight, label: "TessMarket" },
  { href: "/relics", icon: Gem, label: "Relics" },
  { href: "/assets", icon: ListOrdered, label: "Assets" },
  { href: "/orders", icon: History, label: "Orders" },
  { href: "/rewards", icon: Gift, label: "Rewards" },
  { href: "/analytics", icon: BarChart3, label: "Analytics" },
  { href: "/agents", icon: Bot, label: "TessAgents" },
  { href: "/support", icon: Headphones, label: "Support" },
  { href: "/settings", icon: Settings, label: "Settings" },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="flex w-16 flex-col items-center gap-1 border-r border-[var(--border-glow)] bg-[rgba(5,7,10,0.95)] py-4">
      <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg bg-gradient-to-br from-[var(--accent-cyan)] to-[var(--accent-violet)]">
        <Hexagon className="h-5 w-5 text-white" />
      </div>
      {navItems.map(({ href, icon: Icon, label }) => (
        <Link
          key={href}
          href={href}
          title={label}
          className={cn(
            "flex h-10 w-10 items-center justify-center rounded-lg transition-all",
            pathname === href
              ? "bg-[rgba(0,242,255,0.15)] text-[var(--accent-cyan)]"
              : "text-[var(--text-muted)] hover:bg-[rgba(0,242,255,0.08)] hover:text-[var(--accent-cyan)]"
          )}
        >
          <Icon className="h-5 w-5" />
        </Link>
      ))}
      <div className="mt-auto flex flex-col items-center gap-1">
        <div className="h-2 w-2 rounded-full bg-[var(--accent-green)] pulse-glow" />
        <span className="text-[8px] text-[var(--text-muted)]">Online</span>
      </div>
    </aside>
  );
}
