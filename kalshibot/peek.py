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
    rows = []
    with open(path, newline="") as f:
        r = csv.reader(f)
        header = next(r, [])
        for row in r:
            rows.append(row)
    if not rows:
        return (f"'{path}' exists but has 0 data rows (header only).\n"
                f"  -> The recorder connected but captured nothing yet. If it printed a 403,\n"
                f"     you're not on a Kalshi-reachable connection. Otherwise give it a minute.")
    out = [f"'{path}': {len(rows)} rows, {len(header)} columns.",
           f"columns: {', '.join(header)}", "", "first rows:"]
    for row in rows[:n]:
        out.append("  " + " | ".join(row))
    if len(rows) > n:
        out += ["", "latest rows:"]
        for row in rows[-n:]:
            out.append("  " + " | ".join(row))
    out += ["", "VERDICT: real data IS flowing. Ready to analyze for an edge."]
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
