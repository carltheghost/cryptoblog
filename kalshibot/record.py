"""Read-only market-data recorder. Gathers the raw data an edge search needs.

It polls Kalshi market data (NO trading, NO orders) and appends a CSV row per
market per poll: quotes, last price, volume, open interest, and order-book
imbalance. Point it at the short-term crypto series and/or any explicit tickers
(e.g. a perpetual contract once you give me its ticker).

    python -m kalshibot.record --series KXBTC --minutes 120 --out btc.csv

Perpetual futures (launched 2026-05-29) are a SEPARATE, leveraged margin product
with their own API spec and base URL -- not the binary yes/no event markets, so
the structured CSV columns mostly won't apply. Use --base + --raw to capture them
schema-agnostically once you have a ticker:

    python -m kalshibot.record --base https://external-api.kalshi.com/trade-api/v2 \
        --ticker <PERP_TICKER> --raw perp.jsonl --out perp.csv --minutes 120

If Kalshi returns HTTP 403 you're on a blocked network -- run from your own PC.
This module never places an order.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
from datetime import datetime, timezone

from .kalshi_client import (KalshiClient, DEFAULT_CRYPTO_SERIES,
                            PERP_TICKERS, PERPS_BASE_URL)
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


def record(series: list[str], tickers: list[str], minutes: int, poll: float, out: str,
           base: str | None = None, raw: str | None = None):
    client = KalshiClient(base_url=base) if base else KalshiClient()
    print(f"[record] {client.base_url}  ->  {out}" + (f"  (+raw {raw})" if raw else ""))
    try:
        print(f"[record] exchange status: {client.exchange_status()}")
    except Exception as e:
        print(f"[record] cannot reach Kalshi ({e}). If this is a 403, run from your own PC.")
        return

    new_file = not os.path.exists(out)
    raw_f = open(raw, "a") if raw else None
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
                if not m.get("ticker"):
                    continue
                w.writerow(_row(client, m))
                rows += 1
                if raw_f:   # full JSON per market -- schema-agnostic (good for perps)
                    raw_f.write(json.dumps({"ts": datetime.now(timezone.utc).isoformat(),
                                            "market": m}) + "\n")
            f.flush()
            if raw_f:
                raw_f.flush()
            print(f"[record] {datetime.now().strftime('%H:%M:%S')}  "
                  f"markets={len(markets)}  rows_total={rows}")
            time.sleep(poll)
    if raw_f:
        raw_f.close()
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
    ap.add_argument("--base", default=None,
                    help="override base URL, e.g. https://external-api.kalshi.com/trade-api/v2 "
                         "for perpetuals")
    ap.add_argument("--raw", default=None,
                    help="also dump full market JSON per poll to this .jsonl file "
                         "(schema-agnostic; use this for perpetuals)")
    ap.add_argument("--perps", action="store_true",
                    help="probe all known perpetual tickers (BTCPERP confirmed; the "
                         "rest are candidates -- misses are skipped) on the perps host, "
                         "with raw JSON capture on")
    args = ap.parse_args()
    series = args.series if args.series is not None else DEFAULT_CRYPTO_SERIES
    tickers = list(args.ticker)
    base, raw = args.base, args.raw
    if args.perps:
        tickers += [t for t in PERP_TICKERS if t not in tickers]
        base = base or PERPS_BASE_URL
        raw = raw or "kalshi_perps.jsonl"
        series = args.series if args.series is not None else []  # perps host: skip event series
    record(series, tickers, args.minutes, args.poll, args.out, base, raw)


if __name__ == "__main__":
    main()
