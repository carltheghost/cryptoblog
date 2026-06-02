"""Offline backtest. Runs WITHOUT network so you can see the economics now.

It simulates many 15-minute BTC target markets with a realistic random walk,
derives the binary contract price from distance-to-target and remaining time,
applies a bid/ask spread, and runs the momentum strategy through the paper
account with honest fees.

The purpose is not to "prove the bot works" -- it's to show what high-frequency
trading on near-efficient markets actually does to a balance once costs are
charged. Run it:  python -m kalshibot.backtest
"""

from __future__ import annotations

import math
import random
import statistics

from .paper_account import PaperAccount
from .strategy import MomentumStrategy


def _contract_price(distance: float, seconds_left: int, vol_per_sqrt_sec: float) -> float:
    """Fair 'yes' price that BTC ends above target.

    distance = current_price - target (dollars). Uses a normal-CDF approximation
    of P(end > target) given remaining-time volatility. This is the efficient
    price the market would converge to; our strategy has to beat it AFTER costs.
    """
    if seconds_left <= 0:
        return 1.0 if distance > 0 else 0.0
    sigma = vol_per_sqrt_sec * math.sqrt(seconds_left)
    if sigma <= 0:
        return 1.0 if distance > 0 else 0.0
    z = distance / sigma
    # standard normal CDF via erf
    p = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
    return min(max(p, 0.01), 0.99)


def run_one_market(seed: int, *, spread: float, strat: MomentumStrategy,
                   start_balance: float, contracts_per_trade: int) -> dict:
    rng = random.Random(seed)
    duration = 15 * 60                      # 15 minutes, tick per second
    target = 71000.0
    price = target + rng.uniform(-50, 50)
    # ~3% daily vol on a $71k price -> ~$7 per sqrt(second).
    vol_per_sqrt_sec = 7.0

    acct = PaperAccount(cash=start_balance)
    prices = [price]
    market = "BTC-15MIN"

    for t in range(duration):
        price += rng.gauss(0, vol_per_sqrt_sec)
        prices.append(price)
        seconds_left = duration - t
        velocity = price - prices[max(0, len(prices) - 11)]   # ~10s momentum
        distance = price - target

        fair = _contract_price(distance, seconds_left, vol_per_sqrt_sec)
        yes_ask = min(0.99, fair + spread / 2)
        yes_bid = max(0.01, fair - spread / 2)
        no_ask = min(0.99, (1 - fair) + spread / 2)
        no_bid = max(0.01, (1 - fair) - spread / 2)

        yes_key = f"{market}:yes"
        no_key = f"{market}:no"
        have_yes = yes_key in acct.positions
        have_no = no_key in acct.positions
        have = have_yes or have_no

        if have_yes:
            unreal = yes_bid - acct.positions[yes_key].avg_price
        elif have_no:
            unreal = no_bid - acct.positions[no_key].avg_price
        else:
            unreal = 0.0

        sig = strat.decide(velocity=velocity, seconds_left=seconds_left,
                           have_position=have, unrealized=unreal)

        if sig.action == "buy_yes":
            acct.buy(market, "yes", contracts_per_trade, yes_ask, sig.reason)
        elif sig.action == "buy_no":
            acct.buy(market, "no", contracts_per_trade, no_ask, sig.reason)
        elif sig.action == "take_profit":
            if have_yes:
                acct.sell(market, "yes", acct.positions[yes_key].contracts, yes_bid, sig.reason)
            elif have_no:
                acct.sell(market, "no", acct.positions[no_key].contracts, no_bid, sig.reason)

    # settle whatever is left at expiry
    final_up = prices[-1] > target
    if yes_key in acct.positions:
        acct.settle(market, "yes", won=final_up)
    if no_key in acct.positions:
        acct.settle(market, "no", won=not final_up)

    return {
        "end_cash": acct.cash,
        "pnl": acct.cash - start_balance,
        "fees": acct.total_fees_paid,
        "trades": len(acct.fills),
    }


def main(n_markets: int = 200, spread: float = 0.02, contracts: int = 20,
         start_balance: float = 21.0) -> None:
    strat = MomentumStrategy()
    pnls, fees_list, trades_list = [], [], []
    bankroll = start_balance

    for i in range(n_markets):
        res = run_one_market(seed=1000 + i, spread=spread, strat=strat,
                             start_balance=start_balance, contracts_per_trade=contracts)
        pnls.append(res["pnl"])
        fees_list.append(res["fees"])
        trades_list.append(res["trades"])
        bankroll += res["pnl"]

    total_pnl = sum(pnls)
    wins = sum(1 for p in pnls if p > 0)
    print("=" * 64)
    print("KALSHIBOT OFFLINE BACKTEST  (momentum on 15-min BTC target markets)")
    print("=" * 64)
    print(f"markets simulated : {n_markets}")
    print(f"contracts/trade   : {contracts}   spread modeled: {spread*100:.0f}c")
    print(f"avg trades/market : {statistics.mean(trades_list):.1f}")
    print(f"total fees paid   : ${sum(fees_list):.2f}")
    print(f"profitable markets: {wins}/{n_markets} ({100*wins/n_markets:.0f}%)")
    print(f"total P&L         : ${total_pnl:+.2f}")
    print(f"avg P&L / market  : ${statistics.mean(pnls):+.3f}")
    print("-" * 64)
    if total_pnl <= 0:
        print("Result: the strategy LOSES money after costs. The fee + spread")
        print("toll on every trade swamps any edge from watching the ticks.")
        print("This is the expected outcome on near-efficient markets, and it is")
        print("exactly why a paper run must come before any real money.")
    else:
        print("Result: positive in this simulation. Treat with skepticism --")
        print("re-run with realistic spread/fees and live data before trusting it.")
    print("=" * 64)


if __name__ == "__main__":
    main()
