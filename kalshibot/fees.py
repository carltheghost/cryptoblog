"""Honest modeling of Kalshi trading costs.

Two costs eat a high-frequency strategy on these markets:

1. Trading fee. Kalshi's published general fee formula is roughly:
       fee = round_up_to_cent( fee_rate * contracts * price * (1 - price) )
   where price is in dollars (0..1). The default fee_rate is 0.07. Some
   product categories use a different rate, so it's configurable. Verify the
   current rate on Kalshi's fee schedule before trusting live numbers.

2. The bid/ask spread. You buy at the ask and sell at the bid. Crossing it on
   every round-trip is a guaranteed, recurring loss that has nothing to do with
   whether your directional call was right.

The whole point of modeling these is so a "thousands of trades per minute"
strategy gets charged for what it would actually cost.
"""

from __future__ import annotations

import math

DEFAULT_FEE_RATE = 0.07


def trading_fee(price: float, contracts: int, fee_rate: float = DEFAULT_FEE_RATE) -> float:
    """Return the Kalshi trading fee in dollars for a fill.

    price: execution price in dollars (0..1), e.g. 0.82 for an 82c contract.
    contracts: number of contracts in the fill.
    """
    if contracts <= 0:
        return 0.0
    price = min(max(price, 0.0), 1.0)
    raw = fee_rate * contracts * price * (1.0 - price)
    # Kalshi rounds the fee up to the next cent.
    return math.ceil(raw * 100.0) / 100.0


def round_trip_cost(price: float, contracts: int, spread: float,
                    fee_rate: float = DEFAULT_FEE_RATE) -> float:
    """Total cost in dollars to buy then sell `contracts` at ~`price`.

    Includes the fee on both legs plus crossing the `spread` once (in dollars,
    e.g. 0.02 for a 2c spread). This is the toll a churn/"cash-out-and-re-enter"
    loop pays every cycle, win or lose.
    """
    fees = trading_fee(price, contracts, fee_rate) + trading_fee(price, contracts, fee_rate)
    spread_cost = spread * contracts
    return fees + spread_cost
