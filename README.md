# TessChain — Tesseract-Inspired Hybrid Blockchain Platform

A full-stack hybrid crypto ecosystem combining **Centralized (CeFi / MGANGA)** and **Decentralized (DeFi / MWANJESA)** modes, connected by a **Tesseract Hybrid Core** with TessID, HYB bridge, DAG fast payments, and blockchain secure settlement.

## Architecture

```
Centralized Mode (MGANGA)     Tesseract Core      Decentralized Mode (MWANJESA)
├── Spot Trading         ←→   TessID / HYB   ←→   Non-Custodial Wallet
├── Order Book                CeFi ↔ DeFi         DEX Swap
├── Fiat Deposit              DAG Payments          Staking & DAO
├── KYC / AML                 Settlement            Child Chains
├── Custody Vault                                   Living Relics
└── AI Fraud Score                                  Cross-Chain Bridge
```

## Quick Start

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend (Next.js)

```bash
cd apps/web
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### Docker (PostgreSQL + Redis + Backend)

```bash
docker compose up -d
```

### Smart Contracts (Hardhat)

```bash
cd contracts
npm install
npx hardhat compile
```

## Project Structure

```
├── apps/web/           # Next.js dashboard (CeFi + DeFi + Hybrid UI)
├── backend/            # FastAPI API (cefi, defi, identity, market, agents, storage)
├── contracts/          # Solidity (MGANGA, MWANJESA, HYB, LivingRelic, Governance, Staking)
├── packages/shared/    # Shared TypeScript types
└── docker-compose.yml
```

## Key Features

- **Dual-mode UI**: Toggle between Centralized and Decentralized modes
- **TessExchange**: CEX spot trading + DEX swaps
- **Quark Wallet**: Simple and Deep modes with multi-sig, recovery, AI agents
- **TessMarket**: Listings, purchases, receipt-as-relic
- **Living Relics**: Capture → Validate → Mint lifecycle with soul reserve
- **TessAgents**: Administrative and autonomous agent console
- **Tessalink**: Hypergraph relationship index
- **HYB Bridge**: Move assets between CeFi and DeFi economies

## API Endpoints

| Group | Endpoints |
|-------|-----------|
| CeFi | `/api/cefi/account`, `/api/cefi/orders`, `/api/cefi/orderbook/{pair}`, `/api/cefi/fiat/deposit`, `/api/cefi/fraud-score` |
| DeFi | `/api/defi/wallet/{tessId}`, `/api/defi/swap/quote`, `/api/defi/stake`, `/api/defi/bridge`, `/api/defi/relics` |
| Identity | `/api/identity/{tessId}`, `/api/identity/hybrid/balances` |
| Market | `/api/market/listings`, `/api/market/purchase/{id}` |
| Agents | `/api/agents/` |
| Storage | `/api/storage/tesslink/graph`, `/api/storage/shadow-proof/{tokenId}` |
| WebSocket | `/ws/ticker`, `/ws/orderbook/{pair}` |

## Tokens

| Token | Economy | Purpose |
|-------|---------|---------|
| MGANGA | Centralized (PoA) | Merchant payments, CeFi fees |
| MWANJESA | Decentralized (PoS) | Staking, governance participation |
| HYB | Bridge | Cross-economy conversion, governance voting |

## Demo User

- **Username**: TraderOne Pro
- **TessID**: TRD-8F7C-29D1
- **CeFi Balance**: $24,350.68
- **DeFi Balance**: $18,732.41
