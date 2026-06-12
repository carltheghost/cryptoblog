"""Read-only market-data recorder. Gathers the raw data an edge search needs.

It polls Kalshi market data (NO trading, NO orders) and appends a CSV row per
market per poll: quotes, last price, volume, open interest, and order-book
imbalance. Point it at the short-term crypto series and/or any explicit tickers
(e.g. a perpetual contract once you give me its ticker).

    python -m kalshibot.record --series KXBTC --minutes 120 --out btc.csv
    python -m kalshibot.record --ticker KXBTCPERP-... --minutes 120 --out perp.csv

If Kalshi returns HTTP 403 you're on a blocked network -- run from your own PC.
This module never places an order.
"""

from __future__ import annotations

import argparse
import csv
import os
import time
from datetime import datetime, timezone

from .kalshi_client import KalshiClient, DEFAULT_CRYPTO_SERIES
from .run_paper import book_imbalance

FIELDS = ["ts", "ticker", "status", "yes_bid", "yes_ask", "mid", "spread",
          "last_price", "volume", "open_interest", "liquidity", "imbalance"]


def _row(client: KalshiClient, m: dict) -> dict:
    ticker = m.get("ticker", "")
    yes_bid, yes_ask = KalshiClient.best_bid_ask(m)
    mid = (yes_bid + yes_ask) / 2 if (yes_bid and yes_ask) else (yes_bid or yes_ask)
    try:
        imbalance = book_imbalance(client.get_orderbook(ticker))
    except Exception:
        imbalance = 0.0
    return {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "ticker": ticker,
        "status": m.get("status", ""),
        "yes_bid": round(yes_bid, 4),
        "yes_ask": round(yes_ask, 4),
        "mid": round(mid, 4),
        "spread": round(max(0.0, yes_ask - yes_bid), 4),
        "last_price": (m.get("last_price") or 0) / 100.0,
        "volume": m.get("volume", 0),
        "open_interest": m.get("open_interest", 0),
        "liquidity": m.get("liquidity", 0),
        "imbalance": round(imbalance, 4),
    }


def record(series: list[str], tickers: list[str], minutes: int, poll: float, out: str):
    client = KalshiClient()
    print(f"[record] {client.base_url}  ->  {out}")
    try:
        print(f"[record] exchange status: {client.exchange_status()}")
    except Exception as e:
        print(f"[record] cannot reach Kalshi ({e}). If this is a 403, run from your own PC.")
        return

    new_file = not os.path.exists(out)
    deadline = time.time() + minutes * 60
    rows = 0
    with open(out, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            w.writeheader()
        while time.time() < deadline:
            markets = []
            for s in series:
                try:
                    markets += client.list_markets(series_ticker=s, status="open", limit=100)
                except Exception as e:
                    print(f"[record] list {s} failed: {e}")
            for tk in tickers:
                try:
                    markets.append(client.get_market(tk))
                except Exception as e:
                    print(f"[record] get {tk} failed: {e}")
            for m in markets:
                if m.get("ticker"):
                    w.writerow(_row(client, m))
                    rows += 1
            f.flush()
            print(f"[record] {datetime.now().strftime('%H:%M:%S')}  "
                  f"markets={len(markets)}  rows_total={rows}")
            time.sleep(poll)
    print(f"[record] done. {rows} rows -> {out}")


def main():
    ap = argparse.ArgumentParser(description="Read-only Kalshi data recorder (no trading)")
    ap.add_argument("--series", nargs="*", default=None,
                    help=f"series tickers (default: {' '.join(DEFAULT_CRYPTO_SERIES)})")
    ap.add_argument("--ticker", nargs="*", default=[],
                    help="explicit market tickers, e.g. a perpetual contract")
    ap.add_argument("--minutes", type=int, default=120)
    ap.add_argument("--poll", type=float, default=2.0)
    ap.add_argument("--out", default="kalshi_data.csv")
    args = ap.parse_args()
    series = args.series if args.series is not None else DEFAULT_CRYPTO_SERIES
    record(series, args.ticker, args.minutes, args.poll, args.out)


if __name__ == "__main__":
    main()
