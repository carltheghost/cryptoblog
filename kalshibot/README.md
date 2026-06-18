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

The offline backtest charges those costs honestly and ranks four strategies
(200 markets, 20 contracts/trade, 2¢ spread, `signal_edge 0%`):

| strategy | idea | P&L | trades/mkt | fees |
|----------|------|-----|-----------|------|
| `spread` | strong signal + tight book, hold to settle | +$89 | 2.0 | $68 |
| `imbalance` | trade order-book imbalance (here: pure noise) | −$52 | 2.0 | $70 |
| `chronos` | bidirectional bridge + regime + t-stat gate + Kelly | −$247 | 2.0 | $66 |
| `momentum` | ride + take profit, churn | −$870 | 9.2 | $401 |
| `fade` | mean-reversion, fade overextended moves | −$1059 | 7.8 | $479 |

**Even after a serious tune-up, the most complex strategy (`chronos`) still loses
and still can't beat the simplest disciplined one (`spread`).** Its journey is the
real lesson: adding a statistical-significance gate on the drift and forcing it to
hold to settlement (one entry, no churn) cut its loss by ~69% (−$785 → −$247) and
its fees by ~80% ($341 → $66) — *every gain came from doing less, not from more
cleverness.* In trading, complexity is usually how you lose; discipline is the
edge. Two robust takeaways:

1. **Turnover is the enemy.** The churners (`momentum`, `fade`) pay 6–7× the fees
   and lose an order of magnitude more. Trading less is the single biggest lever.
2. **A real signal is what tips you positive.** With `--edge 0` the `imbalance`
   strategy is just noise and loses. Give it genuine predictive power and it
   turns positive:

   ```
   python -m kalshibot.backtest --strategy imbalance --edge 0.4   # +$162
   ```

> ⚠️ **Honesty caveat:** the small *positive* numbers for `spread`/`imbalance`
> are partly a **simulator artifact** — the fair-price model assumes a pure
> random walk, so when the sim injects persistent drift, the "market" misprices
> it and low-turnover strategies exploit that gap. A real market would price the
> drift in. Treat the sim as a tool to see the *fee mechanics*, not as proof any
> strategy makes money. Only a live paper run on real Kalshi data settles that.

## Quick start

```bash
pip install -r requirements.txt

# 1) Offline backtest — runs with no network, shows the economics:
python -m kalshibot.backtest

# 2) Live PAPER run — real Kalshi prices, simulated fills, zero real money:
python -m kalshibot.run_paper --series KXBTC --minutes 30

# 3) Web dashboard — neural-network style control deck at http://localhost:8765
python -m kalshibot.webui

# 4) Personal assistant — talk to the bot in plain English on your PC:
python -m kalshibot.assistant

# 5) Multi-agent arena — many strategies compete on paper, with a leaderboard:
python -m kalshibot.multiagent --agents 11 --markets 60

# 6) Record real market data (read-only, no trading) for an edge search:
python -m kalshibot.record --series KXBTC --minutes 120 --out btc.csv
# ...or a live paper session that logs every decision tick:
python -m kalshibot.run_paper --series KXBTC --strategy imbalance --record ticks.csv
```

### Data collection (`kalshibot.record` + `run_paper --record`)

`record.py` is a **read-only** recorder: it polls Kalshi market data (quotes,
last price, volume, open interest, order-book imbalance) and appends a CSV row
per market per poll. No orders, ever. Point it at the crypto series, or at any
explicit `--ticker` (e.g. a perpetual contract once you supply its ticker).
`run_paper --record FILE` additionally logs every paper decision tick. From the
assistant, just say *"start trading"* or *"collect data"*. Run these on a
Kalshi-reachable machine — they exit cleanly with a 403 message otherwise.

### Multi-agent arena (`kalshibot.multiagent`)

Spawns many agents — one per strategy plus parameter variants — and runs them on
the **same** simulated market so they compete fairly, then prints a leaderboard.
This is the honest take on "more agents = better": more agents help you *discover*
which approach survives fees; they do **not** multiply a losing bet. In practice
every agent still loses after costs, and the high-turnover ones lose most — the
arena just surfaces the least-bad. You can spawn it from the assistant too:
*"spawn 11 agents"*. Paper/sim only.

### Personal assistant (`kalshibot.assistant`)

A local, natural-language control deck. Say things like *"start the spread
strategy"*, *"how am I doing?"*, *"run a backtest of chronos at edge 0.5"*,
*"which strategy is best?"*, *"open the dashboard"*. It runs **fully offline with
zero setup** via a deterministic command understander, and **auto-upgrades to
real conversational replies** if it detects either:

- a local **Ollama** server at `http://localhost:11434` (fully offline LLM), or
- an **`ANTHROPIC_API_KEY`** in your environment (uses the Claude API).

With no LLM it's a fast natural-language *command* assistant, not a chatbot — and
it controls the same in-process sim engine. Paper/sim only: it never places real
orders.

#### Using a local Hermes (or any Ollama) model

The assistant **auto-detects** your installed models and prefers a Hermes one if
present — you don't have to configure anything. If chat isn't working:

1. In one terminal: `ollama serve`
2. Pull a model if you have none: `ollama pull hermes3`
3. In the assistant, type `doctor` — it reports whether Ollama is up, which models
   you have, and which one it will chat with.
4. To force a specific model: `OLLAMA_MODEL=your-model-name python -m kalshibot.assistant`

One-step install: run `bash setup.sh` (macOS/Linux) or double-click `setup.bat`
(Windows). It installs dependencies, checks for Ollama/Hermes, and runs `doctor`.

### Web dashboard (`kalshibot.webui`)

A localhost control deck (stdlib only, no pip installs) that renders the agents
as a live "neural network" — Market Feed → Momentum → Risk/Fees → Account →
Notifier — with pulses firing along the edges on every trade, a live BTC-vs-
target chart, a **strategy dropdown** (momentum/fade/spread/imbalance, switch
live), a **signal-edge slider** to dial the imbalance signal's predictive power,
a live book-imbalance readout, and an **equity-vs-cumulative-fees overlay** so
the cost bleed is impossible to miss.
Sliders start/pause/reset and tune the strategy in real time. Runs on a built-in
**simulation feed** so it works offline. Paper/sim only — no order leaves the machine.

> If Kalshi returns HTTP 403, you're on a blocked network (some clouds/datacenters
> are geofenced). Run from your own machine. Paper mode needs **no API key**.

## Files

| File | What it does |
|------|--------------|
| `fees.py` | Honest Kalshi fee + spread model (the costs that kill churn). |
| `paper_account.py` | Simulated account: cash, positions, settlement, P&L, trade log. |
| `strategy.py` | Five strategies (momentum / fade / spread / imbalance / chronos) + registry. |
| `kalshi_client.py` | Read-only market-data client. `place_order` is disabled. |
| `backtest.py` | Offline simulation of many 15-min markets with realistic vol. |
| `run_paper.py` | Live paper loop against real prices (optional `--record` CSV). |
| `record.py` | Read-only market-data recorder to CSV (no trading). |
| `assistant.py` | Local plain-English assistant (optional Ollama/Claude LLM). |
| `multiagent.py` | Multi-agent arena: many strategies compete on paper + leaderboard. |
| `webui/` | Localhost neural-deck dashboard (engine + stdlib server + canvas UI). |

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
