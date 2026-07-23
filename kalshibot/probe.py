"""Probe one live 15-minute crypto market and print its raw fields.

A focused diagnostic: it finds the nearest-expiry open market in each KX*15M
series and dumps the actual JSON Kalshi returns -- so we can see whether live
quotes are present and under which field names. Read-only, no trading.

    python -m kalshibot.probe
"""

from __future__ import annotations

import json

from .kalshi_client import KalshiClient, CRYPTO_15M_SERIES


def main():
    c = KalshiClient()
    print(f"[probe] {c.base_url}")
    try:
        print(f"[probe] exchange status: {c.exchange_status()}")
    except Exception as e:
        print(f"[probe] cannot reach Kalshi ({e}). Run from your own PC.")
        return

    found_any = False
    for series in CRYPTO_15M_SERIES:
        try:
            ms = c.list_markets(series_ticker=series, status="open", limit=50)
        except Exception as e:
            print(f"[probe] {series}: list failed -> {e}")
            continue
        print(f"\n=== {series}: {len(ms)} open markets ===")
        if not ms:
            continue
        found_any = True
        ms.sort(key=lambda m: m.get("close_time", ""))
        m = ms[0]
        tk = m.get("ticker")
        print(f"nearest market: {tk}   closes: {m.get('close_time')}")
        # The single-market endpoint usually carries the freshest quote fields.
        try:
            full = c.get_market(tk)
        except Exception as e:
            print(f"  get_market failed: {e}")
            full = m
        for k in ("yes_bid", "yes_ask", "no_bid", "no_ask", "last_price",
                  "volume", "open_interest", "liquidity", "status"):
            print(f"  {k:14}= {full.get(k)}")
        try:
            ob = c.get_orderbook(tk)
            print(f"  orderbook    = {json.dumps(ob)[:300]}")
        except Exception as e:
            print(f"  orderbook failed: {e}")
        # show the full raw object once so we learn any unexpected field names
        print("  --- full raw market JSON (first 1200 chars) ---")
        print("  " + json.dumps(full, indent=2)[:1200].replace("\n", "\n  "))
        break  # one good example is enough

    if not found_any:
        print("\n[probe] No open KX*15M markets right now. Either it's outside the hours "
              "Kalshi runs these (try again during US daytime), or the series names need "
              "updating. Paste this whole output back so we can adjust.")


if __name__ == "__main__":
    main()
