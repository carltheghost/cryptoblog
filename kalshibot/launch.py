"""One command to run EVERYTHING on your computer at once:

    python -m kalshibot.launch

It starts, together:
  1. the swarm command center  -> http://localhost:8765/swarm  (strategies live)
  2. a read-only data recorder -> kalshi_data.csv   (15-min crypto markets)
  3. a perpetuals recorder      -> kalshi_perps.jsonl (BTCPERP + candidates)

The dashboard always runs (simulation). The recorders gather REAL Kalshi data if
your machine can reach Kalshi; otherwise they print a 403 and stop, harmlessly.
Nothing here places a real order.
"""

from __future__ import annotations

import argparse
import threading
import time
import webbrowser

from . import record
from .kalshi_client import DEFAULT_CRYPTO_SERIES, PERP_TICKERS, PERPS_BASE_URL
from .webui import server as web


def _recorder(series, tickers, minutes, out, base, raw):
    try:
        record.record(series, tickers, minutes, 2.0, out, base, raw)
    except Exception as e:
        print(f"[launch] recorder ({out}) stopped: {e}")


def main():
    ap = argparse.ArgumentParser(description="Run the whole kalshibot stack locally")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--minutes", type=int, default=600, help="how long to record")
    ap.add_argument("--no-record", action="store_true", help="dashboard only, no data capture")
    ap.add_argument("--no-open", action="store_true")
    args = ap.parse_args()

    print("=" * 60)
    print(" kalshibot — full local launch")
    print("=" * 60)

    if not args.no_record:
        # 15-minute crypto markets -> CSV
        threading.Thread(target=_recorder, args=(
            DEFAULT_CRYPTO_SERIES, [], args.minutes, "kalshi_data.csv", None, None),
            daemon=True).start()
        # perpetuals -> raw JSONL on the perps host
        threading.Thread(target=_recorder, args=(
            [], list(PERP_TICKERS), args.minutes, "kalshi_perps.csv",
            PERPS_BASE_URL, "kalshi_perps.jsonl"), daemon=True).start()
        print("[launch] data recorders started (kalshi_data.csv, kalshi_perps.*)")
        time.sleep(0.5)

    url = f"http://localhost:{args.port}/swarm"
    print(f"[launch] swarm command center -> {url}")
    print("[launch] SIMULATION dashboard + read-only recording. No real orders.")
    if not args.no_open:
        try:
            webbrowser.open(url)
        except Exception:
            pass

    # hand off to the web server (blocking)
    import sys
    sys.argv = ["kalshibot.webui", "--port", str(args.port), "--no-open"]
    web.main()


if __name__ == "__main__":
    main()
