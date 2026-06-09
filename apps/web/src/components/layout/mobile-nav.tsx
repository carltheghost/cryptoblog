"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  TrendingUp,
  Dices,
  Wallet,
  Infinity,
  MoreHorizontal,
} from "lucide-react";
import { cn } from "@/lib/utils";

const mobileItems = [
  { href: "/", icon: LayoutDashboard, label: "Home" },
  { href: "/trade", icon: TrendingUp, label: "Trade" },
  { href: "/casino", icon: Dices, label: "Casino" },
  { href: "/wallet", icon: Wallet, label: "Wallet" },
  { href: "/omniverse", icon: Infinity, label: "Omni" },
  { href: "/market", icon: MoreHorizontal, label: "More" },
];

export function MobileNav() {
  const pathname = usePathname();

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around border-t border-[var(--border-glow)] bg-[rgba(5,7,10,0.98)] px-2 py-2 md:hidden">
      {mobileItems.map(({ href, icon: Icon, label }) => (
        <Link
          key={href}
          href={href}
          className={cn(
            "flex flex-col items-center gap-0.5 rounded-lg px-2 py-1 text-[9px] transition-colors",
            pathname === href
              ? "text-[var(--accent-cyan)]"
              : "text-[var(--text-muted)]"
          )}
        >
          <Icon className="h-5 w-5" />
          <span>{label}</span>
        </Link>
      ))}
    </nav>
  );
}
