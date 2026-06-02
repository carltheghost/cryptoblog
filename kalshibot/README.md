# kalshibot — honest paper-trading + backtest harness for Kalshi crypto markets

This is **not** an auto-trading money machine, and it deliberately does not place
real orders. It's a tool to test, on paper and on history, whether a strategy on
Kalshi's short-term crypto target markets (BTC/ETH/SOL/XRP/DOGE/ADA/LINK 15-min
"target" markets) actually makes money **after fees and spread** — *before* a cent
of real money is risked.

## Read this first

The "watch the ticks, buy Up/Down, cash out, repeat thousands of times" idea
doesn't work, and the code here shows why:

- The Up%/Down% you see in the app **is the price** — the crowd already priced in
  the chart you're looking at. There's no free signal in it.
- "Cash out and re-enter" is not arbitrage. Every round-trip pays the **bid/ask
  spread plus a trading fee**. Do it thousands of times and you pay that toll
  thousands of times.
- "Thousands/millions of trades in minutes" is impossible anyway — Kalshi rate-
  limits orders to a few per second on standard tiers.

The offline backtest charges those costs honestly. On near-efficient 15-minute
markets, momentum churn **loses money** — that's the expected result, not a bug.

## Quick start

```bash
pip install -r requirements.txt

# 1) Offline backtest — runs with no network, shows the economics:
python -m kalshibot.backtest

# 2) Live PAPER run — real Kalshi prices, simulated fills, zero real money:
python -m kalshibot.run_paper --series KXBTC --minutes 30

# 3) Web dashboard — neural-network style control deck at http://localhost:8765
python -m kalshibot.webui
```

### Web dashboard (`kalshibot.webui`)

A localhost control deck (stdlib only, no pip installs) that renders the agents
as a live "neural network" — Market Feed → Momentum → Risk/Fees → Account →
Notifier — with pulses firing along the edges on every trade, a live BTC-vs-
target chart, and sliders to start/pause/reset and tune the strategy in real
time. Runs on a built-in **simulation feed** so it works offline. It is paper/sim
only — no order ever leaves the machine.

> If Kalshi returns HTTP 403, you're on a blocked network (some clouds/datacenters
> are geofenced). Run from your own machine. Paper mode needs **no API key**.

## Files

| File | What it does |
|------|--------------|
| `fees.py` | Honest Kalshi fee + spread model (the costs that kill churn). |
| `paper_account.py` | Simulated account: cash, positions, settlement, P&L, trade log. |
| `strategy.py` | The momentum strategy from the screenshots. Just a signal. |
| `kalshi_client.py` | Read-only market-data client. `place_order` is disabled. |
| `backtest.py` | Offline simulation of many 15-min markets with realistic vol. |
| `run_paper.py` | Live paper loop against real prices. |

## Secrets

Credentials are **never** hardcoded. Copy `.env.example` to `.env` (git-ignored)
and set them there. If you ever pasted a real Kalshi key or Telegram bot token
into a file, **rotate it now** — assume it's compromised.

## Going live (only after a profitable paper run)

`kalshi_client.place_order` raises on purpose. Enabling real-money trading needs:

1. RSA request signing with your API key + private key (`KALSHI-ACCESS-*` headers).
2. Hard risk limits: max position, max daily loss, kill-switch.
3. A paper run that shows a **positive edge after costs** — otherwise live trading
   just loses real money faster.

Until that paper run is green, leave it off.
