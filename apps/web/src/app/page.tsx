"use client";

import { SpotTrading } from "@/components/cefi/spot-trading";
import { OrderBook } from "@/components/cefi/order-book";
import { FiatDeposit, ComplianceStatus } from "@/components/cefi/fiat-compliance";
import { FraudScore, CustodyVault, CefiStats } from "@/components/cefi/fraud-custody";
import { NonCustodialWallet, DexSwap } from "@/components/defi/wallet-swap";
import { StakingPanel, DaoVote } from "@/components/defi/staking-dao";
import { ChildChain, DefiPools, LivingRelicsGrid, CrossChainBridge } from "@/components/defi/pools-relics-bridge";
import { TesseractCore } from "@/components/hybrid/tesseract-core";
import { usePlatformStore } from "@/store/platform";
import { cn } from "@/lib/utils";

export default function DashboardPage() {
  const { mode } = usePlatformStore();

  return (
    <div className="grid grid-cols-12 gap-3">
      {/* CeFi Column */}
      <div className={cn("col-span-12 space-y-3 lg:col-span-4", mode === "decentralized" && "opacity-60")}>
        <div className="grid grid-cols-2 gap-3">
          <SpotTrading />
          <OrderBook />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FiatDeposit />
          <ComplianceStatus />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <FraudScore />
          <CustodyVault />
        </div>
        <CefiStats />
      </div>

      {/* Hybrid Core */}
      <div className="col-span-12 lg:col-span-3">
        <TesseractCore />
      </div>

      {/* DeFi Column */}
      <div className={cn("col-span-12 space-y-3 lg:col-span-5", mode === "centralized" && "opacity-60")}>
        <div className="grid grid-cols-2 gap-3">
          <NonCustodialWallet />
          <DexSwap />
        </div>
        <div className="grid grid-cols-2 gap-3">
          <StakingPanel />
          <DaoVote />
        </div>
        <div className="grid grid-cols-3 gap-3">
          <ChildChain />
          <DefiPools />
          <CrossChainBridge />
        </div>
        <LivingRelicsGrid />
      </div>
    </div>
  );
}
