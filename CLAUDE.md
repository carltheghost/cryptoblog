# CLAUDE.md — kalshibot project handoff

This file orients any Claude Code session (especially **local** Claude Code running
on the user's Windows PC at `C:\Users\carlg\cryptoblog`) so it can continue the
work seamlessly. Read this first.

## What this project is

`kalshibot` — an **honest** paper-trading + research toolkit for Kalshi's short-term
crypto markets (the 15-minute BTC/ETH/SOL/XRP/DOGE/BNB/HYPE up-down markets) and,
later, perpetual futures. It exists to find out — *before any real money* — whether
any tradeable edge exists after fees. Everything runs locally; nothing here places
a real order.

## The single most important fact

**No strategy here has shown a profit after fees.** Across dozens of backtests and a
live multi-agent swarm, every strategy loses to fees on zero-edge data. Simulated
"profit" only appears when the `signal_edge` slider is turned up — i.e. when you
*assume* an edge that hasn't been proven on real data. Do not present simulated
green numbers as if the bot makes money, and do not enable real-money trading until
real data proves a positive edge after costs. The user has seen viral X/Twitter
"$100k Claude bot" posts — those are scams (like+RT+follow+DM funnels with fake
dashboards). Keep the user safe: be honest, never hype.

## Hard rules

- **No real-money order placement.** `kalshi_client.place_order` raises on purpose.
  Do not implement live trading until a paper run shows positive edge after costs,
  and even then only with explicit user confirmation + risk limits.
- **No hardcoded secrets.** Credentials come from env / `.env` (git-ignored). The
  original `godframe_ganka.py` leaked a Telegram token + Kalshi key — treat as
  compromised; user should rotate them.
- Work on branch `claude/kalshi-trading-bot-AXZ1d`; commit + push; PR #2 is open.

## How to run it (Windows PowerShell, in this folder)

```
pip install -r requirements.txt
python -m kalshibot.launch          # swarm dashboard + data recording (all 7 cryptos)
python -m kalshibot.record --minutes 20   # just record real market data -> kalshi_data.csv
python -m kalshibot.peek            # report: how many rows have LIVE quotes
python -m kalshibot.assistant       # plain-English control; uses local Ollama/Hermes if running
python -m kalshibot.backtest        # offline strategy ranking (no network)
python -m kalshibot.multiagent --agents 11   # arena leaderboard
```

Dashboards: `http://localhost:8765/` (single agent) and `/swarm` (command center).

## Modules

- `strategy.py` — 5 strategies: momentum, fade, spread, imbalance, chronos
  (chronos = bidirectional Brownian-bridge + regime + t-stat gate + Kelly). The
  least-turnover strategies lose least; complexity does not help.
- `fees.py` — Kalshi fee + spread model (the costs that kill churn).
- `paper_account.py` — simulated account (cash, positions, settlement, P&L).
- `backtest.py` — offline simulation + strategy ranking; `--edge` sets assumed signal.
- `kalshi_client.py` — read-only market data; `DEFAULT_CRYPTO_SERIES` = the 7
  `KX<COIN>15M` liquid series. `place_order` disabled.
- `record.py` — read-only recorder -> CSV; skips dead/illiquid markets; `--perps`.
- `peek.py` — cross-platform data inspector (replaces `head`).
- `run_paper.py` — live paper loop on real prices (`--record` to log ticks).
- `multiagent.py` — many agents compete on one market + leaderboard.
- `webui/` — engine (single agent), swarm (command center), stdlib server.
- `assistant.py` — local NL assistant; auto-detects Ollama/Hermes or ANTHROPIC_API_KEY.

## Current status (update this as you go)

- ✅ Data pipeline works on the user's PC (Kalshi reachable — no 403 there).
- ✅ Recorder now targets the liquid `KX<COIN>15M` series (earlier it grabbed
  illiquid hourly strike ladders that returned all-zero quotes).
- ⏳ Need a capture during **active US hours** to confirm live quotes flow, then
  analyze whether order-book imbalance predicts the 15-min outcome after fees.
- ❓ Perpetuals: bare tickers 404 on `/markets/{ticker}`; the perps API is separate
  and unverified. Opt-in via `--perps`; don't spam.

## The next real step

Capture real `KX*15M` data with live quotes, then write an analysis that measures:
does `imbalance` (or any feature) at decision time predict which side settles, by
more than the round-trip cost? If yes → carefully build on it. If no → say so
plainly. That answer, on real data, is the whole game.
