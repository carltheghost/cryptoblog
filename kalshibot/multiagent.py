"""Multi-agent paper arena.

Spawns many agents -- each its own strategy/params -- and runs them in parallel
on the *same* simulated market so they compete fairly. Prints a leaderboard.

This is the honest version of "more agents = better": more agents help you
*discover* which approach survives fees, not multiply a losing bet. Every agent
trades on paper. No real money, ever.

    python -m kalshibot.multiagent --agents 8 --markets 60 --edge 0.0
"""

from __future__ import annotations

import argparse
import random
import statistics
from dataclasses import dataclass

from .paper_account import PaperAccount
from .strategy import StrategyContext, make_strategy, STRATEGIES
from .backtest import _contract_price

DURATION = 15 * 60
VOL = 7.3


@dataclass
class AgentSpec:
    label: str
    strategy: str
    entry_velocity: float = 25.0
    take_profit: float = 0.06


def default_roster(n: int) -> list[AgentSpec]:
    """One agent per strategy, then parameter variants as n grows (up to ~25)."""
    roster = [AgentSpec(name, name) for name in STRATEGIES]
    for ev in (15.0, 35.0, 45.0, 55.0):
        for name in STRATEGIES:
            roster.append(AgentSpec(f"{name}-{int(ev)}", name, entry_velocity=ev))
    return roster[:max(1, n)]


def _gen_market(seed: int, signal_edge: float):
    """Generate one shared 15-minute market: target, price path, imbalance series."""
    rng = random.Random(seed)
    target = 71000.0
    price = target + rng.uniform(-50, 50)
    prices = [price]
    imb = [0.0]
    drift = 0.0
    for _ in range(DURATION):
        drift = drift * 0.92 + rng.gauss(0, 1.6)
        price += drift + rng.gauss(0, 6.0)
        prices.append(price)
        true_sig = max(-1.0, min(1.0, drift / 8.0))
        imb.append(max(-1.0, min(1.0,
                   signal_edge * true_sig + (1 - signal_edge) * rng.uniform(-1, 1))))
    return target, prices, imb


def _simulate(spec: AgentSpec, target, prices, imb, spread, contracts, start_balance):
    """Run one agent through one shared market path. Returns end P&L + stats."""
    acct = PaperAccount(cash=start_balance)
    strat = make_strategy(spec.strategy, spec.entry_velocity, spec.take_profit)
    market = "BTC-15MIN"

    for t in range(DURATION):
        S = prices[t + 1]
        seconds_left = DURATION - t
        velocity = S - prices[max(0, (t + 1) - 10)]
        fair = _contract_price(S - target, seconds_left, VOL)
        yes_ask = min(0.99, fair + spread / 2)
        yes_bid = max(0.01, fair - spread / 2)
        no_ask = min(0.99, (1 - fair) + spread / 2)

        yk, nk = f"{market}:yes", f"{market}:no"
        have_yes, have_no = yk in acct.positions, nk in acct.positions
        side = "yes" if have_yes else "no" if have_no else None
        if have_yes:
            unreal = yes_bid - acct.positions[yk].avg_price
        elif have_no:
            unreal = (1 - yes_ask) - acct.positions[nk].avg_price
        else:
            unreal = 0.0

        ctx = StrategyContext(velocity=velocity, seconds_left=seconds_left,
                              have_position=side is not None, side_held=side,
                              unrealized=unreal, fair=fair, spread=spread,
                              imbalance=imb[t + 1], prices=tuple(prices[max(0, t - 88):t + 2]),
                              price=S, target=target, seconds_total=DURATION)
        sig = strat.decide(ctx)
        n = max(1, int(round(contracts * sig.size_frac)))
        if sig.action == "buy_yes":
            acct.buy(market, "yes", n, yes_ask, sig.reason)
        elif sig.action == "buy_no":
            acct.buy(market, "no", n, no_ask, sig.reason)
        elif sig.action == "take_profit":
            if have_yes:
                acct.sell(market, "yes", acct.positions[yk].contracts, yes_bid, sig.reason)
            elif have_no:
                acct.sell(market, "no", acct.positions[nk].contracts, 1 - yes_ask, sig.reason)

    up = prices[-1] > target
    if f"{market}:yes" in acct.positions:
        acct.settle(market, "yes", won=up)
    if f"{market}:no" in acct.positions:
        acct.settle(market, "no", won=not up)
    return {"pnl": acct.cash - start_balance, "fees": acct.total_fees_paid,
            "trades": len(acct.fills)}


def run_arena(n_agents: int = 8, n_markets: int = 60, spread: float = 0.02,
              contracts: int = 20, signal_edge: float = 0.0,
              start_balance: float = 21.0) -> list[dict]:
    roster = default_roster(n_agents)
    agg = {a.label: {"spec": a, "pnl": 0.0, "fees": 0.0, "trades": 0} for a in roster}
    for i in range(n_markets):
        target, prices, imb = _gen_market(2000 + i, signal_edge)
        for a in roster:
            r = _simulate(a, target, prices, imb, spread, contracts, start_balance)
            agg[a.label]["pnl"] += r["pnl"]
            agg[a.label]["fees"] += r["fees"]
            agg[a.label]["trades"] += r["trades"]
    results = [{"label": k, "strategy": v["spec"].strategy, "pnl": v["pnl"],
                "fees": v["fees"], "trades": v["trades"],
                "trades_per_mkt": v["trades"] / n_markets} for k, v in agg.items()]
    results.sort(key=lambda r: r["pnl"], reverse=True)
    return results


def format_leaderboard(results: list[dict], n_markets: int, signal_edge: float) -> str:
    lines = ["=" * 70,
             f"MULTI-AGENT ARENA  ·  {len(results)} agents · {n_markets} markets · "
             f"signal_edge {signal_edge:.0%}",
             "=" * 70,
             f"{'#':<3}{'agent':<18}{'strategy':<11}{'P&L':>11}"
             f"{'fees':>10}{'trades/mkt':>12}",
             "-" * 70]
    for i, r in enumerate(results, 1):
        lines.append(f"{i:<3}{r['label']:<18}{r['strategy']:<11}"
                     f"{('$%+.2f' % r['pnl']):>11}{('$%.0f' % r['fees']):>10}"
                     f"{r['trades_per_mkt']:>12.1f}")
    lines.append("-" * 70)
    best, worst = results[0], results[-1]
    lines.append(f"WINNER: {best['label']} (${best['pnl']:+.2f})   "
                 f"LOSER: {worst['label']} (${worst['pnl']:+.2f})")
    if best["pnl"] <= 0:
        lines.append("Note: even the winning agent loses after costs at this signal "
                     "edge. More agents found the least-bad one; none found free money.")
    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Multi-agent paper arena (no real money)")
    ap.add_argument("--agents", type=int, default=8)
    ap.add_argument("--markets", type=int, default=60)
    ap.add_argument("--spread", type=float, default=0.02)
    ap.add_argument("--edge", type=float, default=0.0)
    args = ap.parse_args()
    results = run_arena(args.agents, args.markets, args.spread, signal_edge=args.edge)
    print(format_leaderboard(results, args.markets, args.edge))


if __name__ == "__main__":
    main()
