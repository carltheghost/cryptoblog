"""The momentum strategy implied by the screenshots.

The idea in the screenshots: watch the BTC index tick, and when it's moving up
relative to the target, buy "Up" (yes); when moving down, buy "Down" (no).
Optionally take profit early by selling back ("cash out").

This module just produces a signal. It does NOT decide it is profitable -- the
paper account + fee model do that. The honest expectation is that on near-
efficient 15-minute markets this has little to no edge, and the costs in
fees.py will dominate. Run it and look at the realized P&L.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Signal:
    action: str          # "buy_yes", "buy_no", "take_profit", "hold"
    reason: str


@dataclass
class MomentumStrategy:
    # Required move (in dollars of BTC) over the lookback window to act.
    entry_velocity: float = 25.0
    # Close the position once the contract's mid moves this far in our favor.
    take_profit: float = 0.06
    # Don't open new positions in the final seconds (no time to be right).
    min_seconds_left: int = 60

    def decide(self, *, velocity: float, seconds_left: int,
               have_position: bool, unrealized: float) -> Signal:
        """velocity: recent BTC index change in dollars (signed).
        unrealized: current per-contract gain in dollars if we hold a position.
        """
        if have_position:
            if unrealized >= self.take_profit:
                return Signal("take_profit", f"unrealized {unrealized:+.2f} >= tp")
            return Signal("hold", "in position, target not hit")

        if seconds_left < self.min_seconds_left:
            return Signal("hold", "too close to expiry")

        if velocity >= self.entry_velocity:
            return Signal("buy_yes", f"up-momentum {velocity:+.0f}")
        if velocity <= -self.entry_velocity:
            return Signal("buy_no", f"down-momentum {velocity:+.0f}")
        return Signal("hold", "no momentum")
