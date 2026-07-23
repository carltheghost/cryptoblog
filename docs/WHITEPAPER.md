# kalshibot — A Honest Multi-Agent Research Harness for Kalshi Short-Term Crypto Markets

**Status:** research / paper-trading only. No real-money orders are placed anywhere
in this system. Version of record: branch `claude/kalshi-trading-bot-AXZ1d`.

---

## Abstract

kalshibot is a local-first toolkit for investigating whether any tradeable edge
exists in Kalshi's 15-minute crypto "up/down" markets (BTC, ETH, SOL, XRP, DOGE,
BNB, HYPE) **after fees and spread**. It combines a fee-accurate paper-trading
engine, five strategies, an offline backtester, a real-time multi-agent arena, a
read-only market-data recorder, and a local natural-language assistant that runs
against your own LLM (Ollama/Hermes, LM Studio, or an API). Its defining feature is
honesty: across every backtest and live simulation, **no strategy has produced a
profit after costs on zero-edge data.** Simulated profit appears only when an
*assumed* signal edge is dialed in. The project exists to test for a real edge on
real data before any capital is risked — and to say plainly when none is found.

## 1. Motivation

Short-term binary markets look like easy money: a chart ticks up, the "Up" side is
82%, and it feels like free profit. It is not. The displayed price already
incorporates the visible chart; "cashing out and re-entering" pays the bid/ask
spread plus a per-contract fee on every round trip; and high-frequency churn is
rate-limited and fee-dominated. Viral "AI made me $115k" posts are engagement/scam
funnels (like + repost + follow + DM) showing fabricated dashboards. kalshibot is
the sober counterpart: measure first, with real costs, before believing anything.

## 2. Cost model

Two costs dominate and are modeled explicitly (`fees.py`):

- **Trading fee** ≈ `round_up(0.07 · C · p · (1 − p))` per fill, where `p` is the
  price in dollars and `C` the contract count.
- **Spread**: buy at the ask, sell at the bid; each round trip crosses it once.

A strategy must overcome `spread + 2·fee` *per round trip* just to break even.

## 3. Architecture

- **paper_account.py** — cash, positions, settlement at $1/$0, realized P&L, fee
  accounting, full trade log.
- **strategy.py** — five strategies over a common `StrategyContext`:
  *momentum*, *fade* (mean-reversion), *spread* (selective, holds to settlement),
  *imbalance* (order-book signal), and *chronos* (bidirectional Brownian-bridge
  settlement probability + regime/drift estimation with a t-stat significance gate
  + fractional-Kelly sizing).
- **backtest.py** — Monte-Carlo simulation of many 15-minute markets with a
  persistent-drift price process; ranks strategies by P&L after costs; `--edge`
  injects a controllable, *assumed* signal so one can study how much real
  predictive power is required to overcome fees.
- **multiagent.py** — N agents (one per strategy plus parameter variants) compete
  on one shared market with a leaderboard.
- **kalshi_client.py** — read-only market data. `place_order` raises by design.
- **record.py / peek.py / probe.py** — read-only data capture to CSV, a
  cross-platform inspector, and a raw-field diagnostic.
- **webui/** — a localhost "neural deck" (single agent) and a "swarm command
  center" (live multi-agent leaderboard, equity-vs-fees, P&L distribution,
  order-flow gauge, risk metrics, and an honesty banner that states whether the
  green is real or an assumed-edge what-if).
- **assistant.py** — a plain-English local control surface that auto-detects a
  local LLM (Ollama/Hermes, LM Studio / any OpenAI-compatible server) or an API
  key, and otherwise runs as a deterministic command interface.

## 4. Findings (representative, 200 simulated markets, 2¢ spread)

| strategy | turnover | result after costs |
|----------|----------|--------------------|
| spread | ~2 trades/mkt | least-bad / near-breakeven |
| imbalance (edge 0) | ~2 trades/mkt | small loss (noise) |
| chronos | low after t-stat gate | loss; complexity did not help |
| momentum / fade | high (8–9 trades/mkt) | largest losses, dominated by fees |

Two robust conclusions: (1) **turnover is the primary destroyer of returns** —
the churning strategies pay 5–7× the fees and lose an order of magnitude more;
(2) **profitability requires a genuine predictive edge** — the `imbalance`
strategy only turns positive once `--edge` is set above ~0.4, i.e. once the signal
is *assumed* to be real. Any positive number in the simulator is contingent on
that assumption, not a discovery. (Note: small positive low-turnover results are
partly a simulator artifact where the pricing model does not price injected drift;
they are not evidence of a real edge.)

## 5. Method for an actual edge test

Capture real `KX*15M` data with live quotes during active hours, then measure
whether order-book imbalance (or any feature) at decision time predicts which side
settles by **more than the round-trip cost**. A positive, out-of-sample, after-cost
result is the only thing that would justify building further. A negative result is
reported plainly.

## 6. Safety and ethics

- No real-money order placement until a paper run shows positive edge after costs,
  and then only with explicit confirmation and hard risk limits (max position,
  daily-loss kill-switch).
- No hardcoded secrets; credentials come from the environment.
- The system is designed to resist self-deception: the UI labels simulation
  clearly and never presents assumed-edge profit as discovered profit.

## 7. Disclaimer

This is research software for education and pre-trade analysis. It is not financial
advice. Trading involves risk of loss, and perpetual/leveraged products amplify it.
Nothing here has demonstrated a profitable edge.
