"""Edge analysis on recorded real Kalshi data.

The whole point of the project: given real captured quotes, does following the
market's own signal (or any feature) at decision time make money after fees, once
markets settle? This reads kalshi_data.csv, reconstructs each market's lifecycle,
and measures hit-rate and P&L after costs. Honest by construction: if there's no
edge, it says so.

    python -m kalshibot.analyze            # uses kalshi_data.csv
"""

from __future__ import annotations

import collections
import csv
import os


def _f(r: dict, k: str) -> float:
    try:
        return float(r.get(k) or 0)
    except (TypeError, ValueError):
        return 0.0


def analyze(path: str = "kalshi_data.csv") -> str:
    if not os.path.exists(path):
        return f"'{path}' not found. Run the recorder first: python -m kalshibot.record"
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return f"'{path}' is empty."

    by = collections.defaultdict(list)
    for r in rows:
        if r.get("ticker"):
            by[r["ticker"]].append(r)

    settled, quoted_markets = [], 0
    for tk, obs in by.items():
        obs.sort(key=lambda r: r.get("ts", ""))
        if any(_f(o, "mid") > 0 for o in obs):
            quoted_markets += 1
        if len(obs) < 6:
            continue
        last_mid = _f(obs[-1], "mid")
        # consider a market "resolved" if its final mid pinned near 0 or 1
        if not (last_mid <= 0.15 or last_mid >= 0.85):
            continue
        outcome_yes = last_mid >= 0.5
        dec = obs[len(obs) // 2]                 # decision point ~ mid-lifecycle
        dmid, dspread = _f(dec, "mid"), _f(dec, "spread")
        if dmid <= 0 or dmid >= 1:
            continue
        fav_yes = dmid >= 0.5                    # follow the market's own lean
        entry = (dmid + dspread / 2) if fav_yes else (1 - dmid + dspread / 2)
        won = (outcome_yes == fav_yes)
        fee = 0.07 * dmid * (1 - dmid)
        pnl = (1.0 if won else 0.0) - entry - fee
        settled.append({"won": won, "pnl": pnl, "conf": abs(dmid - 0.5)})

    out = [f"ANALYSIS of {path}",
           f"  rows: {len(rows)}   markets: {len(by)}   markets with quotes: {quoted_markets}",
           f"  fully-resolved markets captured: {len(settled)}"]
    if len(settled) < 10:
        out.append("")
        out.append("Not enough RESOLVED markets yet to judge an edge. Keep the recorder")
        out.append("running for a few hours (each 15-min market must open AND close while")
        out.append("recording). Then run this again.")
        return "\n".join(out)

    n = len(settled)
    wins = sum(1 for s in settled if s["won"])
    total_pnl = sum(s["pnl"] for s in settled)
    out += ["",
            f"  decision rule: follow the market's favored side at mid-lifecycle, hold to settle",
            f"  hit rate     : {wins}/{n}  ({100*wins/n:.0f}%)",
            f"  P&L/contract : ${total_pnl/n:+.4f}   total: ${total_pnl:+.3f}",
            ""]
    if total_pnl <= 0:
        out += ["VERDICT: no edge after fees on this data — following the market's own",
                "signal loses to the spread+fee, as expected for an efficient market.",
                "That is the honest result. A real edge would need a feature the price",
                "does NOT already reflect (and it must beat the round-trip cost)."]
    else:
        out += ["VERDICT: positive after fees on this sample. Treat with heavy skepticism —",
                "small samples mislead. Keep collecting and re-run; confirm it holds out",
                "of sample before believing it, and never risk money on one good number."]
    return "\n".join(out)


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Measure edge on recorded Kalshi data")
    ap.add_argument("path", nargs="?", default="kalshi_data.csv")
    print(analyze(ap.parse_args().path))


if __name__ == "__main__":
    main()
