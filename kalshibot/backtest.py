"""Offline backtest. Runs WITHOUT network so you can see the economics now.

It simulates many 15-minute BTC target markets with a realistic random walk,
derives the binary contract price from distance-to-target and remaining time,
applies a bid/ask spread, and runs each strategy through the paper account with
honest fees -- then ranks them best-to-worst by P&L after costs.

    python -m kalshibot.backtest                # compare all strategies
    python -m kalshibot.backtest --strategy fade
"""

from __future__ import annotations

import argparse
import math
import random
import statistics

from .paper_account import PaperAccount
from .strategy import StrategyContext, make_strategy, STRATEGIES


def _contract_price(distance: float, seconds_left: int, vol_per_sqrt_sec: float) -> float:
    """Fair 'yes' price that BTC ends above target (normal-CDF approximation)."""
    if seconds_left <= 0:
        return 1.0 if distance > 0 else 0.0
    sigma = vol_per_sqrt_sec * math.sqrt(seconds_left)
    if sigma <= 0:
        return 1.0 if distance > 0 else 0.0
    z = distance / sigma
    p = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return min(max(p, 0.01), 0.99)


def run_one_market(seed: int, *, spread: float, strategy_name: str,
                   entry_velocity: float, take_profit: float,
                   start_balance: float, contracts_per_trade: int) -> dict:
    rng = random.Random(seed)
    duration = 15 * 60
    target = 71000.0
    price = target + rng.uniform(-50, 50)
    vol_per_sqrt_sec = 7.0                  # ~3% daily vol on a $71k price

    acct = PaperAccount(cash=start_balance)
    strat = make_strategy(strategy_name, entry_velocity, take_profit)
    prices = [price]
    market = "BTC-15MIN"

    for t in range(duration):
        price += rng.gauss(0, vol_per_sqrt_sec)
        prices.append(price)
        seconds_left = duration - t
        velocity = price - prices[max(0, len(prices) - 11)]
        distance = price - target

        fair = _contract_price(distance, seconds_left, vol_per_sqrt_sec)
        yes_ask = min(0.99, fair + spread / 2)
        yes_bid = max(0.01, fair - spread / 2)
        no_ask = min(0.99, (1 - fair) + spread / 2)

        yes_key, no_key = f"{market}:yes", f"{market}:no"
        have_yes, have_no = yes_key in acct.positions, no_key in acct.positions
        side_held = "yes" if have_yes else "no" if have_no else None
        if have_yes:
            unreal = yes_bid - acct.positions[yes_key].avg_price
        elif have_no:
            unreal = (1 - yes_ask) - acct.positions[no_key].avg_price
        else:
            unreal = 0.0

        ctx = StrategyContext(velocity=velocity, seconds_left=seconds_left,
                              have_position=side_held is not None, side_held=side_held,
                              unrealized=unreal, fair=fair, spread=spread)
        sig = strat.decide(ctx)

        if sig.action == "buy_yes":
            acct.buy(market, "yes", contracts_per_trade, yes_ask, sig.reason)
        elif sig.action == "buy_no":
            acct.buy(market, "no", contracts_per_trade, no_ask, sig.reason)
        elif sig.action == "take_profit":
            if have_yes:
                acct.sell(market, "yes", acct.positions[yes_key].contracts, yes_bid, sig.reason)
            elif have_no:
                acct.sell(market, "no", acct.positions[no_key].contracts, 1 - yes_ask, sig.reason)

    final_up = prices[-1] > target
    if f"{market}:yes" in acct.positions:
        acct.settle(market, "yes", won=final_up)
    if f"{market}:no" in acct.positions:
        acct.settle(market, "no", won=not final_up)

    return {"pnl": acct.cash - start_balance, "fees": acct.total_fees_paid,
            "trades": len(acct.fills)}


def evaluate(strategy_name: str, *, n_markets: int, spread: float, contracts: int,
             entry_velocity: float, take_profit: float, start_balance: float) -> dict:
    pnls, fees_list, trades_list = [], [], []
    for i in range(n_markets):
        res = run_one_market(seed=1000 + i, spread=spread, strategy_name=strategy_name,
                             entry_velocity=entry_velocity, take_profit=take_profit,
                             start_balance=start_balance, contracts_per_trade=contracts)
        pnls.append(res["pnl"]); fees_list.append(res["fees"]); trades_list.append(res["trades"])
    return {
        "strategy": strategy_name,
        "total_pnl": sum(pnls),
        "avg_pnl": statistics.mean(pnls),
        "fees": sum(fees_list),
        "avg_trades": statistics.mean(trades_list),
        "win_rate": 100 * sum(1 for p in pnls if p > 0) / n_markets,
    }


def main(n_markets: int = 200, spread: float = 0.02, contracts: int = 20,
         start_balance: float = 21.0, entry_velocity: float = 25.0,
         take_profit: float = 0.06, strategy: str | None = None) -> None:
    names = [strategy] if strategy else list(STRATEGIES.keys())
    results = [evaluate(n, n_markets=n_markets, spread=spread, contracts=contracts,
                        entry_velocity=entry_velocity, take_profit=take_profit,
                        start_balance=start_balance) for n in names]
    results.sort(key=lambda r: r["total_pnl"], reverse=True)

    print("=" * 72)
    print(f"KALSHIBOT BACKTEST  ·  {n_markets} markets · {contracts} contracts/trade · "
          f"{spread*100:.0f}c spread")
    print("=" * 72)
    print(f"{'rank':<5}{'strategy':<11}{'P&L':>12}{'avg/mkt':>10}"
          f"{'fees':>11}{'trades/mkt':>12}{'win%':>7}")
    print("-" * 72)
    for i, r in enumerate(results, 1):
        print(f"{i:<5}{r['strategy']:<11}{('$%+.2f'%r['total_pnl']):>12}"
              f"{('$%+.3f'%r['avg_pnl']):>10}{('$%.2f'%r['fees']):>11}"
              f"{r['avg_trades']:>12.1f}{r['win_rate']:>6.0f}%")
    print("-" * 72)
    best, worst = results[0], results[-1]
    print(f"BEST : {best['strategy']}  (${best['total_pnl']:+.2f}, "
          f"${best['fees']:.2f} fees, {best['avg_trades']:.1f} trades/mkt)")
    if len(results) > 1:
        print(f"WORST: {worst['strategy']}  (${worst['total_pnl']:+.2f}, "
              f"${worst['fees']:.2f} fees, {worst['avg_trades']:.1f} trades/mkt)")
    print()
    if best["total_pnl"] <= 0:
        print("Even the best strategy LOSES after costs. The least-bad one is the")
        print("one that trades least -- fewer round-trips, less spread+fee toll.")
        print("That is the honest takeaway: turnover is the enemy here, not the goal.")
    else:
        print(f"'{best['strategy']}' is positive in simulation. Verify on live paper")
        print("data before trusting it -- a synthetic walk is not the real market.")
    print("=" * 72)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--strategy", choices=list(STRATEGIES.keys()), default=None)
    ap.add_argument("--markets", type=int, default=200)
    ap.add_argument("--contracts", type=int, default=20)
    ap.add_argument("--spread", type=float, default=0.02)
    args = ap.parse_args()
    main(n_markets=args.markets, contracts=args.contracts, spread=args.spread,
         strategy=args.strategy)
