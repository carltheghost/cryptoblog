"""Live PAPER trading loop: real Kalshi market data in, simulated fills out.

No real orders are ever placed. This connects to Kalshi's read-only market-data
endpoints, runs the momentum strategy against live prices, and books fills in a
PaperAccount so you can watch real-world P&L accrue without risking funds.

Run:  python -m kalshibot.run_paper --series KXBTC --minutes 30

If Kalshi returns 403 from your network, run it from your own machine. No API
key is required for paper mode (market data is public).
"""

from __future__ import annotations

import argparse
import time

from .kalshi_client import KalshiClient
from .paper_account import PaperAccount
from .strategy import StrategyContext, make_strategy


def pick_market(client: KalshiClient, series: str) -> dict | None:
    markets = client.list_markets(series_ticker=series, status="open", limit=50)
    # prefer the soonest-closing open market with a live quote
    markets = [m for m in markets if m.get("yes_ask")]
    markets.sort(key=lambda m: m.get("close_time", ""))
    return markets[0] if markets else None


def run(series: str, minutes: int, contracts: int, poll: float,
        strategy: str = "momentum") -> None:
    client = KalshiClient()
    acct = PaperAccount(cash=21.0)
    strat = make_strategy(strategy)

    print(f"[paper] connecting to {client.base_url}")
    try:
        print(f"[paper] exchange status: {client.exchange_status()}")
    except Exception as e:
        print(f"[paper] could not read exchange status ({e}). "
              f"If this is a 403, run from your own machine.")
        return

    deadline = time.time() + minutes * 60
    last_mid = None

    while time.time() < deadline:
        market = pick_market(client, series)
        if not market:
            print(f"[paper] no open {series} market right now; waiting...")
            time.sleep(poll)
            continue

        ticker = market["ticker"]
        m = client.get_market(ticker)
        yes_bid, yes_ask = KalshiClient.best_bid_ask(m)
        mid = (yes_bid + yes_ask) / 2 if (yes_bid and yes_ask) else (yes_bid or yes_ask)
        velocity = 0.0 if last_mid is None else (mid - last_mid) * 1000  # cents->signal
        last_mid = mid

        key_yes, key_no = f"{ticker}:yes", f"{ticker}:no"
        have_yes, have_no = key_yes in acct.positions, key_no in acct.positions
        side_held = "yes" if have_yes else "no" if have_no else None
        if have_yes:
            unreal = yes_bid - acct.positions[key_yes].avg_price
        elif have_no:
            unreal = (1 - yes_ask) - acct.positions[key_no].avg_price
        else:
            unreal = 0.0

        ctx = StrategyContext(velocity=velocity, seconds_left=999,
                              have_position=side_held is not None, side_held=side_held,
                              unrealized=unreal, fair=mid, spread=max(0.0, yes_ask - yes_bid))
        sig = strat.decide(ctx)

        if sig.action == "buy_yes" and yes_ask:
            acct.buy(ticker, "yes", contracts, yes_ask, sig.reason)
        elif sig.action == "buy_no" and yes_bid:
            acct.buy(ticker, "no", contracts, max(0.01, 1 - yes_ask), sig.reason)
        elif sig.action == "take_profit":
            if key_yes in acct.positions:
                acct.sell(ticker, "yes", acct.positions[key_yes].contracts, yes_bid, sig.reason)
            elif key_no in acct.positions:
                acct.sell(ticker, "no", acct.positions[key_no].contracts, max(0.01, 1 - yes_ask), sig.reason)

        print(f"[paper] {ticker} yes {yes_bid:.2f}/{yes_ask:.2f} | {sig.action:11s} "
              f"| {sig.reason:24s} | {acct.summary()}")
        time.sleep(poll)

    print("\n[paper] session over.")
    print(f"[paper] FINAL: {acct.summary()}")


def main() -> None:
    ap = argparse.ArgumentParser(description="Live paper-trade Kalshi crypto markets (no real money).")
    ap.add_argument("--series", default="KXBTC", help="series ticker, e.g. KXBTC")
    ap.add_argument("--minutes", type=int, default=30, help="how long to run")
    ap.add_argument("--contracts", type=int, default=10, help="contracts per trade")
    ap.add_argument("--poll", type=float, default=2.0, help="seconds between polls")
    ap.add_argument("--strategy", default="momentum",
                    choices=["momentum", "fade", "spread"])
    args = ap.parse_args()
    run(args.series, args.minutes, args.contracts, args.poll, args.strategy)


if __name__ == "__main__":
    main()
