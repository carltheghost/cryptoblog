"""Peek at recorded data files, cross-platform (works on Windows/Mac/Linux).

    python -m kalshibot.peek

Shows whether your recorders are actually capturing real Kalshi data: row counts,
first/last rows, columns, and a quick health verdict. No more `head` vs
PowerShell headaches.
"""

from __future__ import annotations

import csv
import os


def summary(path: str = "kalshi_data.csv", n: int = 5) -> str:
    if not os.path.exists(path):
        return (f"'{path}' does not exist yet.\n"
                f"  -> The recorder hasn't written any data. Most likely it can't reach\n"
                f"     Kalshi (a 403 / not-logged-in / network issue), or it isn't running.\n"
                f"  -> Start it with:  python -m kalshibot.launch")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return (f"'{path}' exists but has 0 data rows (header only).\n"
                f"  -> The recorder connected but captured nothing yet. If it printed a 403,\n"
                f"     you're not on a Kalshi-reachable connection. Otherwise give it a minute.")

    def fnum(r, k):
        try:
            return float(r.get(k, 0) or 0)
        except ValueError:
            return 0.0

    tickers = {r.get("ticker", "") for r in rows}
    quoted = [r for r in rows if fnum(r, "mid") > 0 or fnum(r, "yes_bid") > 0
              or fnum(r, "yes_ask") > 0]
    traded = [r for r in rows if fnum(r, "volume") > 0 or fnum(r, "open_interest") > 0]
    ts = [r.get("ts", "") for r in rows if r.get("ts")]
    span = f"{ts[0]}  ->  {ts[-1]}" if ts else "?"

    out = [f"'{path}': {len(rows)} rows, {len(tickers)} distinct markets.",
           f"time span: {span}",
           f"rows with a LIVE QUOTE : {len(quoted)}  ({100*len(quoted)//max(1,len(rows))}%)",
           f"rows with volume/OI    : {len(traded)}", ""]

    sample = quoted[-n:] if quoted else rows[-n:]
    out.append("sample rows (quoted first):" if quoted else "sample rows (all zero — see below):")
    for r in sample:
        out.append(f"  {r.get('ts','')[-8:]}  {r.get('ticker','')[:28]:<28} "
                   f"bid {r.get('yes_bid','')}  ask {r.get('yes_ask','')}  "
                   f"vol {r.get('volume','')}  imb {r.get('imbalance','')}")
    out.append("")
    if quoted:
        out.append(f"VERDICT: real data IS flowing and {len(quoted)} rows have live quotes. "
                   "Ready to analyze for an edge.")
    else:
        out.append("VERDICT: connection works, but EVERY row is empty (no quotes/volume). "
                   "You captured dead strike markets, or it's a quiet hour with no live "
                   "trading. Re-run the recorder (now filters to active markets): "
                   "python -m kalshibot.record --minutes 30")
    return "\n".join(out)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Peek at recorded Kalshi data (cross-platform)")
    ap.add_argument("path", nargs="?", default="kalshi_data.csv")
    ap.add_argument("-n", type=int, default=5)
    args = ap.parse_args()
    print(summary(args.path, args.n))


if __name__ == "__main__":
    main()
